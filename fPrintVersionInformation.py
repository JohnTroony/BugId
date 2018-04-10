import os, platform;
from mColors import *;
import mProductDetails;
from mWindowsAPI import fsGetPythonISA, oSystemInfo;
from oConsole import oConsole;


def fPrintProductDetails(oProductDetails, bIsMainProduct):
  if oProductDetails.oLicense:
    oConsole.fPrint(
      u"\u2502 \u2219 ", bIsMainProduct and HILITE or INFO, oProductDetails.sProductName,
      NORMAL, " version: ", INFO, str(oProductDetails.oProductVersion),
      NORMAL, ".",
    );
  elif oProductDetails.bHasTrialPeriod and oProductDetails.bInTrialPeriod:
    oConsole.fPrint(
      u"\u2502 \u2219 ", bIsMainProduct and HILITE or INFO, oProductDetails.sProductName,
      NORMAL, " version: ", INFO, str(oProductDetails.oProductVersion),
      NORMAL, " ", WARNING, "(in trial period)",
      NORMAL, ".",
    );
  else:
    oConsole.fPrint(
      u"\u2502 \u2219 ", bIsMainProduct and HILITE or INFO, oProductDetails.sProductName,
      NORMAL, " version: ", INFO, str(oProductDetails.oProductVersion),
      NORMAL, " ", ERROR, "(no valid license found)",
      NORMAL, ".",
    );
  if oProductDetails.oLatestProductVersion:
    if oProductDetails.bVersionIsPreRelease:
      oConsole.fPrint(
        u"\u2502     You are running a ", HILITE, "pre-release", NORMAL, " version:",
        " the latest released version is ", INFO, str(oProductDetails.oLatestProductVersion), NORMAL, ".",
      );
    elif not oProductDetails.bVersionIsUpToDate:
      oConsole.fPrint(
        u"\u2502     You are running an ", WARNING, "old", NORMAL, " version:",
        " the latest released version is  ", HILITE, str(oProductDetails.oLatestProductVersion), NORMAL, ",",
        " available at ", HILITE, oProductDetails.oRepository.sLatestVersionURL, NORMAL, ".",
      );

def fasProductNamesOutput(asProductNames, uNormalColor):
  asOutput = [INFO, asProductNames[0]];
  if len(asProductNames) == 2:
    asOutput.extend([uNormalColor, " and ", INFO, asProductNames[1]]);
  elif len(asProductNames) > 2:
    for sProductName in asProductNames[1:-1]:
      asOutput.extend([uNormalColor, ", ", INFO, sProductName]);
    asOutput.extend([uNormalColor, ", and ", INFO, asProductNames[-1]]);
  return asOutput;

def fPrintVersionInformation(bCheckForUpdates = True):
  # Read product details for rs and all modules it uses.
  aoProductDetails = mProductDetails.faoGetProductDetailsForAllLoadedModules();
  oMainProductDetails = mProductDetails.foGetProductDetailsForMainModule();
  if bCheckForUpdates:
    bEverythingUpToDate = True;
    uCheckedProductCounter = 0;
    for oProductDetails in aoProductDetails:
      oConsole.fProgressBar(
        uCheckedProductCounter * 1.0 / len(aoProductDetails),
        "Checking %s for updates..." % oProductDetails.sProductName,
      );
      try:
        oProductDetails.oLatestProductDetailsFromRepository;
      except Exception as oException:
        oConsole.fPrint(
          ERROR, u"- Version check for ", ERROR_INFO, oProductDetails.sProductName,
          ERROR, " failed: ", ERROR_INFO, str(oException),
        );
      else:
        bEverythingUpToDate &= oProductDetails.bVersionIsUpToDate; 
      uCheckedProductCounter += 1;
  oConsole.fLock();
  try:
    oConsole.fPrint(
      u"\u250C\u2500 ", INFO, "Version information", NORMAL, " ", sPadding = u"\u2500"
    );
    # Output the BugId product information first, then its dependencies:
    fPrintProductDetails(oMainProductDetails, True);
    dasProductNames_by_oLicense = {};
    asProductNamesInTrial = [];
    asUnlicensedProductNames = [];
    
    for oProductDetails in aoProductDetails:
      if oProductDetails != oMainProductDetails:
        fPrintProductDetails(oProductDetails, False);
      if oProductDetails.oLicense:
        dasProductNames_by_oLicense.setdefault(oProductDetails.oLicense, []).append(oProductDetails.sProductName);
      elif oProductDetails.bHasTrialPeriod and oProductDetails.bInTrialPeriod:
        asProductNamesInTrial.append(oProductDetails.sProductName);
      else:
        asUnlicensedProductNames.append(oProductDetails.sProductName);
    
    oConsole.fPrint(
      u"\u2502 \u2219 ", INFO, "Windows",
      NORMAL, " version: ", INFO, oSystemInfo.sOSName,
      NORMAL, " release ", INFO, oSystemInfo.sOSReleaseId,
      NORMAL, ", build ", INFO, oSystemInfo.sOSBuild,
      NORMAL, " ", INFO, oSystemInfo.sOSISA,
      NORMAL, ".",
    );
    oConsole.fPrint(
      u"\u2502 \u2219 ", INFO, "Python",
      NORMAL, " version: ", INFO, str(platform.python_version()),
      NORMAL, " ", INFO, fsGetPythonISA(),
      NORMAL, ".",
    );
    
    oConsole.fPrint(
      u"\u251C\u2500 ", INFO, "License information", NORMAL, " ", sPadding = u"\u2500",
    );
    if dasProductNames_by_oLicense:
      oConsole.fPrint(
        NORMAL, u"\u2502 This system is registered with id ", INFO, mProductDetails.fsGetSystemId(), NORMAL, " on the license server",
      );
    for (oLicense, asProductNames) in dasProductNames_by_oLicense.items():
      oConsole.fPrint(
        u"\u2502 \u2219 License ", INFO, oLicense.sAuthentication,
        NORMAL, " for ", INFO, oLicense.sUsageTypeDescription, 
        NORMAL, " of ", INFO, oLicense.asProductNames[0], 
        NORMAL, " by ", INFO, oLicense.sLicenseeName,
        NORMAL, " covers the following products:",
      );
      oConsole.fPrint(*(
        [
          u"\u2502     ",
        ] + fasProductNamesOutput(asProductNames, NORMAL) + [
          NORMAL, "."
        ]
      ));
    if asProductNamesInTrial:
      oConsole.fPrint(*(
        [
          u"\u2502 \u2219"
        ] + fasProductNamesOutput(asProductNamesInTrial, WARNING)  + [
          WARNING, " ", len(asProductNamesInTrial) == 1 and "is in its" or "are in their", " trial period."
        ]
      ));
    if asUnlicensedProductNames:
      oConsole.fPrint(*(
        [
          u"\u2502 \u2219"
        ] + fasProductNamesOutput(asUnlicensedProductNames, ERROR)  + [
          ERROR, " ", len(asUnlicensedProductNames) == 1 and "has" or "have", " exceeded their trial period and ",
          len(asUnlicensedProductNames) == 1 and "is" or "are", " not currently covered by a valid, active license."
        ]
      ));
#    if bCheckForUpdates and bEverythingUpToDate:
#      oConsole.fPrint(
#        u"\u2502 All modules are up-to-date.",
#      );
    oConsole.fPrint(
      u"\u2514", sPadding = u"\u2500",
    );
    oConsole.fPrint();
  finally:
    oConsole.fUnlock();

  (asLicenseErrors, asLicenseWarnings) = mProductDetails.ftasGetLicenseErrorsAndWarnings();
  if asLicenseErrors:
    oConsole.fLock();
    try:
      oConsole.fPrint(ERROR, u"\u250C\u2500", ERROR_INFO, " Software license error ", ERROR, sPadding = u"\u2500");
      for sLicenseError in asLicenseErrors:
        oConsole.fPrint(ERROR, u"\u2502 ", ERROR_INFO, sLicenseError);
      oConsole.fPrint(ERROR, u"\u2514", sPadding = u"\u2500");
    finally:
      oConsole.fUnlock();
  if asLicenseWarnings:
    oConsole.fLock();
    try:
      oConsole.fPrint(WARNING, u"\u250C\u2500", WARNING_INFO, " Software license warning ", WARNING, sPadding = u"\u2500");
      for sLicenseWarning in asLicenseWarnings:
        oConsole.fPrint(WARNING, u"\u2502 ", WARNING_INFO, sLicenseWarning);
      oConsole.fPrint(WARNING, u"\u2514", sPadding = u"\u2500");
    finally:
      oConsole.fUnlock();
