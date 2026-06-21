from tinydb import Query, TinyDB
from pathlib import Path
import os
import argparse
import logging
logger = logging.getLogger("hairloss")
from datetime import date

from .evaluate import *
from .visuals import *
from .gallery import *

models = ["llava:7b", "gemma4:12b", "qwen3-vl:8b", "ministral-3:8b"]
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    parser.add_argument("--generate_with_llava", action="store_true", help="Generate values with llava:7b")
    parser.add_argument("--generate_with_gemma", action="store_true", help="Generate values with gemma4:12b")
    parser.add_argument("--generate_with_qwen", action="store_true", help="Generate values with qwen3-vl:8b")
    parser.add_argument("--generate_with_ministral", action="store_true", help="Generate values with ministral-3:8b")
    parser.add_argument("--generate_averages", action="store_true", help="Generate averages values")
    parser.add_argument("--generate_gallery", action="store_true", help="Generate gallery")
    parser.add_argument("--generate_visuals", action="store_true", help="Graph the values in multiple plots.")




    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    IMAGES = Path(os.environ.get("HAIRLOSS_IMAGES", "Images")) or Path("./Images")
    
    if args.generate_with_llava:
        evaluate(IMAGES, "llava:7b", 10, 10)
    if args.generate_with_gemma:
        evaluate(IMAGES, "gemma4:12b", 3, 90) # gemma takes much more time as it use thinking, so we reduce the repetitions
    if args.generate_with_qwen:
        evaluate(IMAGES, "qwen3-vl:8b", 1, 180)
    if args.generate_with_ministral:
        evaluate(IMAGES, "ministral-3:8b", 10, 10)
    if args.generate_averages:
        db = TinyDB(path.abspath(path.join(IMAGES, "../hairlineResults.json")))
        q = Query()
        # average
        for image in db:
            sumModels = 0
            sumModelsNormalized = 0
            for key in image.keys():
                if key in models:
                    sumModels += image[key + "WithoutUnsure"]
                    sumModelsNormalized += image[key + "Normalized"]
            image["average"] = sumModels/len(models)
            image["averageNormalized"] = sumModelsNormalized/len(models)
            logger.info(f"Image {image["filename"]}: average = {str(image["average"])} averageNormalized = {str(image["averageNormalized"])}")
            db.upsert(image, q.filename == image)
    if args.generate_gallery:
        gallery(IMAGES)
    if args.generate_visuals:
        # args are models, withClean, withNormalized, withRaw, image_path, filepath, doSave, doShow, doRegression, doCorrelation, angle (array of "t", "f" and "l")

        # all angles
        plotHairline(["llava:7b", "gemma4:12b", "qwen3-vl:8b", "ministral-3:8b"], False, False, True, IMAGES, "rawDataAllModelsAllAngles.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["t", "f", "l"], False, False)
        plotHairline(["llava:7b", "gemma4:12b", "qwen3-vl:8b", "ministral-3:8b"], True, False, False, IMAGES, "withCleanDataAllModelsAllAngles.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["t", "f", "l"], False, False)
        plotHairline(["llava:7b", "gemma4:12b", "qwen3-vl:8b", "ministral-3:8b"], False, True, False, IMAGES, "withNormalizedAllModelsAllAngles.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["t", "f", "l"], False, False)
        plotHairline(["llava:7b"], True, False, True, IMAGES, "dataLlavaAllAngles.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["t", "f", "l"], False, False)
        plotHairline(["gemma4:12b"], True, False, True, IMAGES, "dataGemmaAllAngles.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["t", "f", "l"], False, False)
        plotHairline(["qwen3-vl:8b"], True, False, True, IMAGES, "dataQwenAllAngles.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["t", "f", "l"], False, False)
        plotHairline(["ministral-3:8b"], True, False, True, IMAGES, "dataMinistralAllAngles.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["t", "f", "l"], False, False)
        plotHairline(["ministral-3:8b"], True, True, False, IMAGES, "dataMinistralNormalizedAllAngles.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["t", "f", "l"], False, False)
        plotHairline(["llava:7b"], True, True, False, IMAGES, "dataLLavaNormalizedAllAngles.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["t", "f", "l"], False, False)
        plotHairline(["gemma4:12b"], True, True, False, IMAGES, "dataGemmaNormalizedAllAngles.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["t", "f", "l"], False, False)
        plotHairline(["qwen3-vl:8b"], True, True, False, IMAGES, "dataQwenNormalizedAllAngles.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["t", "f", "l"], False, False)
        plotHairline(["average"], False, True, False, IMAGES, "dataAverageNormalizedAllAngles.pdf", True, False, True, True, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["t", "f", "l"], False, False)
        plotHairline(["average"], False, False, True, IMAGES, "dataAverageAllAngles.pdf", True, False, True, True, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["t", "f", "l"], False, False)


        # top angle
        plotHairline(["llava:7b", "gemma4:12b", "qwen3-vl:8b", "ministral-3:8b"], False, False, True, IMAGES, "rawDataAllModelsTopAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["t"], False, False)
        plotHairline(["llava:7b", "gemma4:12b", "qwen3-vl:8b", "ministral-3:8b"], True, False, False, IMAGES, "withCleanDataAllModelsTopAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["t"], False, False)
        plotHairline(["llava:7b", "gemma4:12b", "qwen3-vl:8b", "ministral-3:8b"], False, True, False, IMAGES, "withNormalizedAllModelsTopAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["t"], False, False)
        plotHairline(["llava:7b"], True, False, True, IMAGES, "dataLlavaTopAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["t"], False, False)
        plotHairline(["gemma4:12b"], True, False, True, IMAGES, "dataGemmaTopAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["t"], False, False)
        plotHairline(["qwen3-vl:8b"], True, False, True, IMAGES, "dataQwenTopAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["t"], False, False)
        plotHairline(["ministral-3:8b"], True, False, True, IMAGES, "dataMinistralTopAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["t"], False, False)
        plotHairline(["ministral-3:8b"], True, True, False, IMAGES, "dataMinistralNormalizedTopAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["t"], False, False)
        plotHairline(["llava:7b"], True, True, False, IMAGES, "dataLLavaNormalizedTopAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["t"], False, False)
        plotHairline(["gemma4:12b"], True, True, False, IMAGES, "dataGemmaNormalizedTopAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["t"], False, False)
        plotHairline(["qwen3-vl:8b"], True, True, False, IMAGES, "dataQwenNormalizedTopAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["t"], False, False)
        plotHairline(["average"], False, True, False, IMAGES, "dataAverageNormalizedTopAngle.pdf", True, False, True, True, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["t"], False, False)
        plotHairline(["average"], False, False, True, IMAGES, "dataAverageTopAngle.pdf", True, False, True, True, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["t"], False, False)


        # face angle
        plotHairline(["llava:7b", "gemma4:12b", "qwen3-vl:8b", "ministral-3:8b"], False, False, True, IMAGES, "rawDataAllModelsFaceAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["f"], False, False)
        plotHairline(["llava:7b", "gemma4:12b", "qwen3-vl:8b", "ministral-3:8b"], True, False, False, IMAGES, "withCleanDataAllModelsFaceAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["f"], False, False)
        plotHairline(["llava:7b", "gemma4:12b", "qwen3-vl:8b", "ministral-3:8b"], False, True, False, IMAGES, "withNormalizedAllModelsFaceAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["f"], False, False)
        plotHairline(["llava:7b"], True, False, True, IMAGES, "dataLlavaFaceAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["f"], False, False)
        plotHairline(["gemma4:12b"], True, False, True, IMAGES, "dataGemmaFaceAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["f"], False, False)
        plotHairline(["qwen3-vl:8b"], True, False, True, IMAGES, "dataQwenFaceAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["f"], False, False)
        plotHairline(["ministral-3:8b"], True, False, True, IMAGES, "dataMinistralFaceAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["f"], False, False)
        plotHairline(["ministral-3:8b"], True, True, False, IMAGES, "dataMinistralNormalizedFaceAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["f"], False, False)
        plotHairline(["llava:7b"], True, True, False, IMAGES, "dataLLavaNormalizedFaceAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["f"], False, False)
        plotHairline(["gemma4:12b"], True, True, False, IMAGES, "dataGemmaNormalizedFaceAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["f"], False, False)
        plotHairline(["qwen3-vl:8b"], True, True, False, IMAGES, "dataQwenNormalizedFaceAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["f"], False, False)
        plotHairline(["average"], False, True, False, IMAGES, "dataAverageNormalizedFaceAngle.pdf", True, False, True, True, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["f"], False, False)
        plotHairline(["average"], False, False, True, IMAGES, "dataAverageFaceAngle.pdf", True, False, True, True, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["f"], False, False)

        # lateral angle
        plotHairline(["llava:7b", "gemma4:12b", "qwen3-vl:8b", "ministral-3:8b"], False, False, True, IMAGES, "rawDataAllModelsLateralAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["l"], False, False)
        plotHairline(["llava:7b", "gemma4:12b", "qwen3-vl:8b", "ministral-3:8b"], True, False, False, IMAGES, "withCleanDataAllModelsLateralAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["l"], False, False)
        plotHairline(["llava:7b", "gemma4:12b", "qwen3-vl:8b", "ministral-3:8b"], False, True, False, IMAGES, "withNormalizedAllModelsLateralAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["l"], False, False)
        plotHairline(["llava:7b"], True, False, True, IMAGES, "dataLlavaLateralAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["l"], False, False)
        plotHairline(["gemma4:12b"], True, False, True, IMAGES, "dataGemmaLateralAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["l"], False, False)
        plotHairline(["qwen3-vl:8b"], True, False, True, IMAGES, "dataQwenLateralAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["l"], False, False)
        plotHairline(["ministral-3:8b"], True, False, True, IMAGES, "dataMinistralLateralAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["l"], False, False)
        plotHairline(["ministral-3:8b"], True, True, False, IMAGES, "dataMinistralNormalizedLateralAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["l"], False, False)
        plotHairline(["llava:7b"], True, True, False, IMAGES, "dataLLavaNormalizedLateralAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["l"], False, False)
        plotHairline(["gemma4:12b"], True, True, False, IMAGES, "dataGemmaNormalizedLateralAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["l"], False, False)
        plotHairline(["qwen3-vl:8b"], True, True, False, IMAGES, "dataQwenNormalizedLateralAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["l"], False, False)
        plotHairline(["average"], False, True, False, IMAGES, "dataAverageNormalizedLateralAngle.pdf", True, False, True, True, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["l"], False, False)
        plotHairline(["average"], False, False, True, IMAGES, "dataAverageLateralAngle.pdf", True, False, True, True, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["l"], False, False)



        # stress inducing factor since 2023-09-11 (ex: sickness, work or in this case being near an anoying person) to see if there was an influence on the hair loss
        plotHairline(["average"], False, True, False, IMAGES, "dataAverageNormalizedSince2023-09-11AllAngles.pdf", True, False, True, True, date.fromisoformat("2023-09-11"), date.fromisoformat("2050-01-01"), ["t", "f", "l"], False, False)
        plotHairline(["average"], False, True, False, IMAGES, "dataAverageNormalizedSince2023-09-11TopAngles.pdf", True, False, True, True, date.fromisoformat("2023-09-11"), date.fromisoformat("2050-01-01"), ["t"], False, False)
        plotHairline(["average"], False, True, False, IMAGES, "dataAverageNormalizedSince2023-09-11FaceAngles.pdf", True, False, True, True, date.fromisoformat("2023-09-11"), date.fromisoformat("2050-01-01"), ["f"], False, False)
        plotHairline(["average"], False, True, False, IMAGES, "dataAverageNormalizedSince2023-09-11LateralAngles.pdf", True, False, True, True, date.fromisoformat("2023-09-11"), date.fromisoformat("2050-01-01"), ["l"], False, False)

        # from our testing top is a less reliable angle
        # top and lateral angle
        plotHairline(["llava:7b", "gemma4:12b", "qwen3-vl:8b", "ministral-3:8b"], False, False, True, IMAGES, "rawDataAllModelsFaceAndLateralAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["f","l"], False, False)
        plotHairline(["llava:7b", "gemma4:12b", "qwen3-vl:8b", "ministral-3:8b"], True, False, False, IMAGES, "withCleanDataAllModelsFaceAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["f","l"], False, False)
        plotHairline(["llava:7b", "gemma4:12b", "qwen3-vl:8b", "ministral-3:8b"], False, True, False, IMAGES, "withNormalizedAllModelsFaceAndLateralAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["f","l"], False, False)
        plotHairline(["llava:7b"], True, False, True, IMAGES, "dataLlavaFaceAndLateralAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["f","l"], False, False)
        plotHairline(["gemma4:12b"], True, False, True, IMAGES, "dataGemmaFaceAndLateralAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["f","l"], False, False)
        plotHairline(["qwen3-vl:8b"], True, False, True, IMAGES, "dataQwenFaceAndLateralAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["f","l"], False, False)
        plotHairline(["ministral-3:8b"], True, False, True, IMAGES, "dataMinistralFaceAndLateralAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["f","l"], False, False)
        plotHairline(["ministral-3:8b"], True, True, False, IMAGES, "dataMinistralNormalizedFaceAndLateralAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["f","l"], False, False)
        plotHairline(["llava:7b"], True, True, False, IMAGES, "dataLLavaNormalizedFaceAndLateralAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["f","l"], False, False)
        plotHairline(["gemma4:12b"], True, True, False, IMAGES, "dataGemmaNormalizedFaceAndLateralAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["f","l"], False, False)
        plotHairline(["qwen3-vl:8b"], True, True, False, IMAGES, "dataQwenNormalizedFaceAndLateralAngle.pdf", True, False, False, False, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["f","l"], False, False)
        plotHairline(["average"], False, True, False, IMAGES, "dataAverageNormalizedFaceAndLateralAngle.pdf", True, False, True, True, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["f","l"], False, False)
        plotHairline(["average"], False, False, True, IMAGES, "dataAverageFaceAndLateralAngle.pdf", True, False, True, True, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["f","l"], False, False)

        plotHairline(["average"], False, True, False, IMAGES, "dataAverageNormalizedSince2023-09-11FaceAndLateralAngles.pdf", True, False, True, True, date.fromisoformat("2023-09-11"), date.fromisoformat("2050-01-01"), ["f","l"], False, False)

        # final plots
        plotHairline(["average"], False, True, False, IMAGES, "averagedDataAverageNormalizedFaceAndLateralAngle.pdf", True, False, True, True, date.fromisoformat("1983-04-01"), date.fromisoformat("2050-01-01"), ["f","l"], True, False)
        plotHairline(["average"], False, True, False, IMAGES, "averagedDataAverageNormalizedSince2023-09-11FaceAndLateralAngles.pdf", True, False, True, True, date.fromisoformat("2023-09-11"), date.fromisoformat("2050-01-01"), ["f","l"], True, False)


