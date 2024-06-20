from math import exp


def DoubleSidedCB(x, params):
    norm = params[0]
    mu = params[1]
    widthL = abs(params[2])
    widthR = abs(params[3])
    alphaL = params[4]
    alphaR = params[5]
    nL = params[6]
    nR = params[7]

    signAL = 1.0 if nL > 0.0 else -1.

    signAR = 1.0 if nR > 0.0 else -1.


    # print mu, widthL, widthR, alphaL, alphaR, nL, nR
    AL = signAL * pow(abs(nL)/abs(alphaL), nL) * exp(- abs(alphaL*alphaL)/2.0)
    AR = signAR * pow(abs(nR)/abs(alphaR), nR) * exp(- abs(alphaR*alphaR)/2.0)
    BL = nL/abs(alphaL) - abs(alphaL)
    BR = nR/abs(alphaR) - abs(alphaR)

    diffL = (x[0]-mu)/widthL
    diffR = (x[0]-mu)/widthR

    if diffL < -alphaL:
        result = AL * pow(abs(BL-diffL), -nL)
    elif diffL > -alphaL and diffL < 0.:
        result = exp(-0.5 * diffL*diffL)
    elif diffR > 0. and diffR < alphaR:
        result = exp(-0.5 * diffR*diffR)
    elif diffR > alphaR:
        result = AR * pow(abs(BR+diffR), -nR)
    else:
        print diffL, diffR, alphaL, alphaR
    return norm*result


def OneSidedCB(x, params):
    norm = params[0]
    mu = params[1]
    width = abs(params[2])
    alphaL = params[3]
    alphaR = params[4]
    nL = params[5]
    nR = params[6]

    signAL = 1.0
    if nL < 0.0 and not (nL % 2) == 0:
        signAL = -1

    signAR = 1.0
    if nR < 0.0 and not (nR % 2) == 0:
        signAR = -1

    # print mu, widthL, widthR, alphaL, alphaR, nL, nR
    AL = signAL * pow(abs(nL)/abs(alphaL), nL) * exp(- abs(alphaL*alphaL)/2.0)
    AR = signAR * pow(abs(nR)/abs(alphaR), nR) * exp(- abs(alphaR*alphaR)/2.0)
    BL = nL/abs(alphaL) - abs(alphaL)
    BR = nR/abs(alphaR) - abs(alphaR)

    diff = (x[0]-mu)/width

    if diff < -alphaL:
        result = AL * pow(abs(BL-diff), -nL)
    elif diff > -alphaL and diff < alphaR:
        result = exp(-0.5 * diff*diff)
    elif diff > alphaR:
        result = AR * pow(abs(BR+diff), -nR)
    else:
        print diff, alphaL, alphaR
    return norm*result
