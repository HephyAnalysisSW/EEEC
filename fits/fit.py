import argparse
import re
import os

import Analysis.Tools.syncer
from array import array
from EEEC.Tools.user import plot_directory
from RootTools.plot.helpers import copyIndexPHP
from scipy.signal import find_peaks

plot_directory_ = os.path.join(plot_directory, 'EEEC' )
if not os.path.exists( plot_directory_ ): 
    os.makedirs( plot_directory_ )
copyIndexPHP( plot_directory_ )

parser = argparse.ArgumentParser(description="Parse x, y, e values from a specified text file.")
parser.add_argument("--filename", type=str, help="Path to the input text file.")
args = parser.parse_args()

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
from ROOT import RooFit, RooRealVar, RooCBShape, RooAddPdf, RooDataHist, RooPlot, RooFormulaVar, RooArgSet, RooArgList, RooPolynomial

class Data:
    def __init__(self, x_data, y_data, e_data):
        self.x_data = x_data
        self.y_data = y_data
        self.e_data = e_data
        self.fit_result = None

    def fit2(self, line_number=0, x_low=None, x_high=None):
        # Get the data for a specific line
        x = self.x_data[line_number]
        y = self.y_data[line_number]
        e = self.e_data[line_number]

        fit_range_min = min(x) if x_low is None else x_low
        fit_range_max = max(x) if x_high is None else x_high

        # Define the observable (x variable)
        x_var = RooRealVar("x", "x", fit_range_min, fit_range_max)

        # Define the parameters for the DCB function with initial guesses
        amplitude = RooRealVar("amplitude", "amplitude", max(y), 0, 1.5 * max(y))
        mean = RooRealVar("mean", "mean", sum(x) / len(x), fit_range_min, fit_range_max)
        sigma = RooRealVar("sigma", "sigma", (fit_range_max - fit_range_min) / 10, 0.001, (fit_range_max - fit_range_min) / 2)
        alpha_left = RooRealVar("alpha_left", "alpha_left", 1.5, 0.01, 50)
        n_left = RooRealVar("n_left", "n_left", 2, 0.01, 10)
        alpha_right = RooRealVar("alpha_right", "alpha_right", 1.5, 0.01, 50)
        n_right = RooRealVar("n_right", "n_right", 2, 0.01, 10)

       # Create a RooFormulaVar to make alpha_right effectively negative for the right tail
        alpha_right_neg = ROOT.RooFormulaVar("alpha_right_neg", "-@0", ROOT.RooArgList(alpha_right))

        # Define the left and right Crystal Ball functions
        cb_left = RooCBShape("cb_left", "Crystal Ball Left", x_var, mean, sigma, alpha_left, n_left)
        cb_right = RooCBShape("cb_right", "Crystal Ball Right", x_var, mean, sigma, alpha_right_neg, n_right)

        # Combine the left and right functions into a double-sided Crystal Ball PDF
        fraction = RooRealVar("fraction", "fraction of left component", 0.5, 0, 1)
        dcb_pdf = RooAddPdf("dcb_pdf", "Double-sided Crystal Ball PDF", cb_left, cb_right, fraction)

        # Define the constant offset model as a RooPolynomial
        offset = RooRealVar("offset", "constant offset", min(y), min(y), max(y))
        offset_model = RooPolynomial("offset_model", "Constant Offset", x_var, RooArgList(offset))

        # Define the fraction for the DCB component (1 - offset_fraction will be used for the offset)
        dcb_fraction = RooRealVar("dcb_fraction", "fraction of DCB component", 0.9, 0, 1)

        # Combine the DCB and offset using RooAddPdf
        dcb_with_offset = RooAddPdf("dcb_with_offset", "DCB with offset", RooArgList(dcb_pdf, offset_model), RooArgList(dcb_fraction))

      # Fill the data into a RooDataHist format, taking y as the observed value and e as errors
        hist = ROOT.TH1F("data_hist", "Data Histogram", len(x), fit_range_min, fit_range_max)
        for bin_index, (xi, yi, ei) in enumerate(zip(x, y, e)):
            hist.SetBinContent(1+bin_index, yi)
            hist.SetBinError(1+bin_index, ei)

        data = RooDataHist("data", "dataset with errors", ROOT.RooArgList(x_var), hist)

        # Perform the fit
        fit_result = dcb_with_offset.fitTo(data, RooFit.Save())

        # Plotting the fit results
        frame = x_var.frame(RooFit.Title("Double-sided Crystal Ball Fit with Offset"))
        data.plotOn(frame)
        dcb_with_offset.plotOn(frame)

        # Display the plot on a canvas
        canvas = ROOT.TCanvas("canvas", "Double-sided Crystal Ball Fit", 800, 600)
        frame.Draw()

        # Set the y-axis minimum to the lowest y value
        frame.SetMinimum(min(y))

        subdir = os.path.join( plot_directory_, "fits2")
        copyIndexPHP(subdir)
        filename = os.path.join( subdir, "fit_{}_{}.png".format(os.path.splitext(args.filename)[0], line_number) )
        canvas.Print(filename)

        # Save the fit result
        self.fit_result = fit_result
        fit_result.Print()

    def fit3(self, line_number=0, x_low=None, x_high=None):
        # Get the data for a specific line
        x = self.x_data[line_number]
        y = self.y_data[line_number]
        e = self.e_data[line_number]
        
        fit_range_min = min(x) if x_low is None else x_low
        fit_range_max = max(x) if x_high is None else x_high

        # Create a TGraphErrors object to store the data points with errors
        n_points = len(x)
        graph = ROOT.TGraphErrors(n_points)
        
        for i in range(n_points):
            graph.SetPoint(i, x[i], y[i])
            graph.SetPointError(i, 0, e[i])
        
        # Step 1: Fit a Gaussian to get initial mean and sigma estimates
        gaussian = ROOT.TF1("gaussian", "gaus", fit_range_min, fit_range_max)
        gaussian.SetParameters(max(y), sum(x) / len(x), (max(x) - min(x)) / 4)
        graph.Fit(gaussian, "Q")  # Silent fit with "Q" option
        
        # Extract the Gaussian fit results
        self.initial_amplitude = gaussian.GetParameter(0)
        self.initial_mean = gaussian.GetParameter(1)
        self.initial_sigma = gaussian.GetParameter(2)

       # Step 2: Define the double-sided Crystal Ball function as a string
        dcb_formula = """
            [7]+(x < [1] - [3]*[2]) * ([0] * pow([4] / fabs([3]), [4]) * exp(-0.5 * [3]*[3]) * 
                                   pow([4] / fabs([3]) - fabs([3]) - (x - [1]) / [2], -[4])) +
            (fabs((x - [1]) / [2]) <= [3]) * ([0] * exp(-0.5 * ((x - [1]) / [2])**2)) +
            (x > [1] + [5]*[2]) * ([0] * pow([6] / fabs([5]), [6]) * exp(-0.5 * [5]*[5]) * 
                                   pow([6] / fabs([5]) - [5] + (x - [1]) / [2], -[6]))
        """
        
        # Step 3: Initialize the TF1 with the DCB formula
        crystal_ball = ROOT.TF1("crystal_ball", dcb_formula, fit_range_min, fit_range_max)
        
        # Set initial guesses based on Gaussian fit results and reasonable tail parameters
        crystal_ball.SetParameters(self.initial_amplitude, self.initial_mean, self.initial_sigma, 1.5, 1, 1.5, 1, 0)

        crystal_ball.FixParameter(3, 100)       
        crystal_ball.FixParameter(4, 0)       
        crystal_ball.FixParameter(5, 100)       
        crystal_ball.FixParameter(6, 0)       
 
        # Parameter names for clarity (optional)
        crystal_ball.SetParNames("Amplitude", "Mean", "Sigma", "Alpha_left", "N_left", "Alpha_right", "N_right", "Offset")
        
        # Step 4: Fit the data with the double-sided Crystal Ball function
        self.fit_result = graph.Fit(crystal_ball, "S")  # "S" option to save fit results
        
        # Store the fitted function
        self.function = crystal_ball

        # Create a TCanvas in goff mode (off-screen)
        canvas = ROOT.TCanvas("canvas", "Fit", 800, 600)
        canvas.SetBatch(True)  # Equivalent to goff mode for saving to file
        
        # Create a TGraphErrors object for plotting
        n_points = len(x)
        graph = ROOT.TGraphErrors(n_points)
        
        for i in range(n_points):
            graph.SetPoint(i, x[i], y[i])
            graph.SetPointError(i, 0, e[i])
        
        # Set graph options
        graph.SetMarkerStyle(20)
        graph.SetMarkerColor(ROOT.kBlue)
        graph.SetTitle("Fit;X;Y")
        
        # Draw the data points and the fit result
        graph.Draw("AP")  # A: Axis, P: Points
        if self.function:
            self.function.SetLineColor(ROOT.kRed)
            self.function.Draw("same")
        
        # Save the canvas to a PNG file
        subdir = os.path.join( plot_directory_, "fits3")
        copyIndexPHP(subdir)
        filename = os.path.join( subdir, "fit_{}_{}.png".format(os.path.splitext(args.filename)[0], line_number) )
        canvas.Print(filename)

    def find_peaks_scipy(self, line_number=0, height=None, prominence=0, width=10, distance=None):
        # Get the data for a specific line
        x = self.x_data[line_number]
        y = self.y_data[line_number]

        # Find peaks using scipy's find_peaks function
        peaks, properties = find_peaks(y, height=height, prominence=prominence, width=width, distance=distance)
        
        # Extract the x and y values of the detected peaks
        peak_x = [x[i] for i in peaks]
        peak_y = [y[i] for i in peaks]

        # Print the peaks found with Python 2 string formatting
        print("Peaks found:")
        for px, py in zip(peak_x, peak_y):
            print("x = {}, y = {}".format(px, py))
        
        # Convert x and y to arrays of type double for TGraph
        x_arr = array("d", x)
        y_arr = array("d", y)

        # Create a ROOT canvas and TGraph for plotting
        canvas = ROOT.TCanvas("canvas", "Detected Peaks", 800, 600)
        graph = ROOT.TGraph(len(x_arr), x_arr, y_arr)
        graph.SetTitle("Peak Detection;X;Y")
        graph.SetMarkerStyle(20)
        graph.SetMarkerColor(ROOT.kBlue)
        graph.Draw("AP")

        # Mark the peaks with a different color
        peak_marker = ROOT.TGraph(len(peak_x))
        for i, (px, py) in enumerate(zip(peak_x, peak_y)):
            peak_marker.SetPoint(i, px, py)
        peak_marker.SetMarkerStyle(22)  # Different marker style for peaks
        peak_marker.SetMarkerColor(ROOT.kRed)
        peak_marker.Draw("P")        # Save the canvas to a PNG file

        subdir = os.path.join( plot_directory_, "peaks")
        copyIndexPHP(subdir)
        filename = os.path.join( subdir, "fit_{}_{}.png".format(os.path.splitext(args.filename)[0], line_number) )
        canvas.Print(filename)
        
        return peak_x, peak_y, properties

    def fit_spline(self, line_number=0,n_spline=300, smoothing_factor=None):
        from scipy.interpolate import CubicSpline
        from scipy.interpolate import UnivariateSpline
        import numpy as np
       # Get the data for a specific line
        x = self.x_data[line_number]
        y = self.y_data[line_number]

        # Fit a smoothing spline to the data with UnivariateSpline
        # The smoothing_factor (s) controls how smooth the spline is; higher values allow more deviation from data points
        spline = UnivariateSpline(x, y, s=smoothing_factor)

        # Generate fitted values for smoother plotting
        x_smooth = np.linspace(min(x), max(x), n_spline)  # Increase to 300 points for a very smooth curve
        y_smooth = spline(x_smooth)

        # Convert data and fitted spline points to arrays for ROOT
        x_arr = array("d", x)
        y_arr = array("d", y)
        x_smooth_arr = array("d", x_smooth)
        y_smooth_arr = array("d", y_smooth)

        # Create a ROOT canvas and TGraph for the original data points
        canvas = ROOT.TCanvas("canvas", "Smoothing Spline Fit", 800, 600)
        graph_data = ROOT.TGraph(len(x_arr), x_arr, y_arr)
        graph_data.SetTitle("Smoothing Spline Fit;X;Y")
        graph_data.SetMarkerStyle(20)
        graph_data.SetMarkerColor(ROOT.kBlue)
        graph_data.Draw("AP")

        # Create a TGraph for the spline fit and overlay it
        graph_spline = ROOT.TGraph(len(x_smooth_arr), x_smooth_arr, y_smooth_arr)
        graph_spline.SetLineColor(ROOT.kRed)
        graph_spline.SetLineWidth(2)
        graph_spline.Draw("L")  # Draw as line
        subdir = os.path.join( plot_directory_, "splines")
        copyIndexPHP(subdir)
        filename = os.path.join( subdir, "fit_{}_{}.png".format(os.path.splitext(args.filename)[0], line_number) )
        canvas.Print(filename)
 
# Example usage:
# Assuming x_data, y_data, e_data are lists of lists from previous script
data = Data(x_data, y_data, e_data)
for line_number in range(len(x_data)):
#    data.fit2(line_number=line_number)
#    data.fit3(line_number=line_number)
#    data.find_peaks_scipy(line_number=line_number)
    #data.fit_spline(line_number=line_number,n_spline=300,smoothing_factor=.00005)# for W
    data.fit_spline(line_number=line_number,n_spline=300,smoothing_factor=.0005)# for top
#
Analysis.Tools.syncer.sync()
