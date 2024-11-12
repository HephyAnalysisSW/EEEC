import argparse
import re

def parse_line(line):
    # Extracts values of the form {x, {y, e}} using regex
    pattern = r"\{([^,]+),\s*\{([^,]+),\s*([^\}]+)\}\}"
    matches = re.findall(pattern, line)
    x_values = []
    y_values = []
    e_values = []
    
    for match in matches:
        x = float(match[0].strip())
        y = float(match[1].strip())
        e = float(match[2].strip())
        
        x_values.append(x)
        y_values.append(y)
        e_values.append(e)
        
    return x_values, y_values, e_values


#def main():
parser = argparse.ArgumentParser(description="Parse x, y, e values from a specified text file.")
parser.add_argument("--filename", type=str, help="Path to the input text file.")
args = parser.parse_args()

x_data = []
y_data = []
e_data = []

with open(args.filename, 'r') as file:
    for line_number, line in enumerate(file):
        x_values, y_values, e_values = parse_line(line)
        x_data.append(x_values)
        y_data.append(y_values)
        e_data.append(e_values)

import ROOT

class Data:
    def __init__(self, x_data, y_data, e_data):
        self.x_data = x_data
        self.y_data = y_data
        self.e_data = e_data
        self.fit_result = None
    
    def fit_crystal_ball(self, line_number=0):
        # Get the data for a specific line
        x = self.x_data[line_number]
        y = self.y_data[line_number]
        e = self.e_data[line_number]
        
        # Create a TGraphErrors object to store the data points with errors
        n_points = len(x)
        graph = ROOT.TGraphErrors(n_points)
        
        for i in range(n_points):
            graph.SetPoint(i, x[i], y[i])
            graph.SetPointError(i, 0, e[i])
        
        # Define the Crystal Ball function
        crystal_ball = ROOT.TF1("crystal_ball", "[0] * ROOT.Math.crystalball_pdf((x - [1]) / [2], [3], [4])", min(x), max(x))
        crystal_ball.SetParameters(1, sum(x)/len(x), 1, 2, 2)  # Initial guesses
        
        # Perform the fit and store the result
        self.fit_result = graph.Fit(crystal_ball, "S")  # S option saves the fit result
        
        # Store the fitted function
        self.crystal_ball = crystal_ball
        return self.fit_result
    
    def draw(self, line_number=0):
        # Get the data for a specific line
        x = self.x_data[line_number]
        y = self.y_data[line_number]
        e = self.e_data[line_number]
        
        # Create a TCanvas to draw on
        canvas = ROOT.TCanvas("canvas", "Crystal Ball Fit", 800, 600)
        
        # Create a TGraphErrors object for plotting
        n_points = len(x)
        graph = ROOT.TGraphErrors(n_points)
        
        for i in range(n_points):
            graph.SetPoint(i, x[i], y[i])
            graph.SetPointError(i, 0, e[i])
        
        # Set graph options
        graph.SetMarkerStyle(20)
        graph.SetMarkerColor(ROOT.kBlue)
        graph.SetTitle("Crystal Ball Fit;X;Y")
        
        # Draw the data points and the fit result
        graph.Draw("AP")  # A: Axis, P: Points
        if self.crystal_ball:
            self.crystal_ball.SetLineColor(ROOT.kRed)
            self.crystal_ball.Draw("same")
        
        # Display the canvas
        canvas.Draw()
        
# Example usage:
# Assuming x_data, y_data, e_data are lists of lists from previous script
data = Data(x_data, y_data, e_data)
fit_result = data.fit_crystal_ball(line_number=0)
data.draw(line_number=0)

