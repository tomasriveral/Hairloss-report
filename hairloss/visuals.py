from tinydb import TinyDB
from datetime import datetime
import matplotlib.pyplot as plt
from os import path
from scipy.stats import spearmanr
import numpy as np
from datetime import date
from logging import getLogger
logger = getLogger("hairloss")

def averageWithDates(dates, values): # average points with same date
    dates = np.array(dates)
    values = np.array(values)
    datesUnique = np.unique(dates)
    valuesUnique = np.array([values[dates == datesCopy].mean() for datesCopy in datesUnique])
    return (datesUnique, valuesUnique)

def plotHairline(models: [str], withClean: bool, withNormalized: bool, withRaw: bool, image_path: str, filepath: str, doSave: bool, doShow: bool, doRegression: bool, doCorrelation: bool, start: date, end: date, angles: [str], doAverage: bool, doPlot: bool):
    db = TinyDB(path.abspath(path.join(image_path, "../hairlineResults.json")))

    if doPlot and (doRegression or doCorrelation):
        raise ValueError("You can't use regression or correlation wit doPlot set to true.")

    if doPlot and not doAverage:
        raise ValueError("doPlot needs doAverage set to True")

    databaseEntry = db.all()
    filteredDatabaseEntry = []
    for entry in databaseEntry:
        # we filter by date
        if start <= date.fromisoformat(entry["filename"][:10]) <= end:
            # and by angles
            for angleType in angles:
                if angleType in entry["filename"]:
                    filteredDatabaseEntry.append(entry)

    dates = [datetime.strptime(d["filename"][:10], "%Y-%m-%d") for d in filteredDatabaseEntry]

    plt.figure(figsize=(12, 6))


    if (doRegression or doCorrelation) and withClean + withNormalized + withRaw != 1:
        raise ValueError(f"With doRegression or doCorrelation exaclty one of withClean, withNormalized or withRaw must be set to true")
    
    values = []

    # plot raw values
    if withRaw:
        for model in models:
            values = [d[model] for d in filteredDatabaseEntry]
            if doAverage:
                dates, values = averageWithDates(dates, values)
            if doPlot:
                plt.plot(dates, values, label=model)
            else:
                plt.scatter(dates, values, label=model)

    # plot without uncertain
    if withClean:
        for model in models:
            key = model + "WithoutUnsure"
            values = [d[key] for d in filteredDatabaseEntry]
            if doAverage:
                dates, values = averageWithDates(dates, values)
            if doPlot:
                plt.plot(dates, values, label=key)
            else:
                plt.scatter(dates, values, label=key)
    if withNormalized:
        for model in models:
            key = model + "Normalized"
            values = [d[key] for d in filteredDatabaseEntry]
            if doAverage:
                dates, values = averageWithDates(dates, values)
            if doPlot:
                plt.plot(dates, values, label=key)
            else:
                plt.scatter(dates, values, label=key)

    if doCorrelation:
        rho, p = spearmanr([d.toordinal() for d in dates], values)
        plt.plot([], [], ' ', label=f"Correlation factor of {rho:-3f} (with p-value of {p:.3g})")

    if doRegression:
        x = np.array([d.toordinal() for d in dates])
        m, b = np.polyfit(x, values, 1)
        plt.plot(dates, m*x + b, label=f"Regression line y={m}*x + {b}")


    plt.xlabel("Dates")
    plt.ylabel("Baldness score")
    plt.title(filepath)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    if doShow:
        plt.show()
    if doSave:
        plt.savefig(filepath, bbox_inches="tight")
    plt.close()
