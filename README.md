# Hairloss report

Initially intended as a joke, but I decided to publish it in case someone wants to reuse it later.

Note : It will only produce the graphs of the receding hairline and a gallery view of each pictures with its relevent score. You will need to write the report yourself.

This project was written in a rush (less than two days before leaving to vacation) and, as such, uses extensively AI (ChatGPT 5.5 free tier). I might (or might not) come back later to polish it a bit.

# Preparation

### Models

You will need to have pulled the models (this will take multiple gigas of storage) :
```
ollama pull llava:7b
ollama pull ministral-3:8b
ollama pull gemma4:12b
ollama pull qwen3-vl:8b
```

This report's strategy is to use multiple models and to repeat multiple time averaging the results. The models used are :
* llava:7b (10x repetitions)
* ministral-3:8b (10x repetitions)
* gemma4:12b (3x repetitions)
* qwen3-vl:8b (1x repetitions)

If you want to change the models or the number of repetitions, a quick run of `rg -C3 {your model here}` should show you where are the changes needed.

### Images

For privacy reason, this repo does not contain the initial dataset of images.

Your dataset needs to :
* focus on thethe person's head. Crop pictures if needed.
* follow this naming logic : `yyyy-mm-dd-nna` where `yyyy-mm-dd` follows [iso 8601](https://en.wikipedia.org/wiki/ISO_8601), `nn` is a number between 00 and 99 (used in cases there are multiple images for the same day and `a` is the angle of the photo (`t` for top, `l` for lateral and `f` for face). If you don't know the exact date, estimate it. There are two helper script in this repo (just fix the shebang and directory paths). `rename.sh` renames all the files (this could break stuff, be careful) into their last modified date. You just need to crop them and add the number and angles. `checkNaming.sh` checks if the files are correctly named (works on `.png` for other format adapt the regex).
* You should try to use the best quality pictures.


### Graphs

You can browse the repo for an example of the graphs and the tex file for the gallery.

One feature of this project is that you can focus on the period after one stres--inducing event (difficult work, sickness, annoying person, ...) that you hypothesize it will impact the rate of hairloss.
You can change this date by running `sed -i "s|2023-09-11|{Put here your date}|g" ./hairloss/main.py`

If you have multiple such events, you will need to manually modify the code in `./hairloss/main.py`.

# Usage

## On [NixOS](https://nixos.org/)

Clear the examples graphs : `rm *.pdf`

You must set the path to the images directory as the nix store doesn't work with relative paths.
```
sed -i "s|PathToYourLocalGitClone/Images|$(pwd)/Images|g" flake.nix
```

Generate the values. This might take some time as it uses multiple ML models and repeats the prompt for less noise. For comparison, this took a few hours on my RTX3070ti.

Note : if you want to run on a GPU you must replace the `ollama` package by a [gpu-specific one](https://search.nixos.org/packages?type=packages&query=ollama) by running `sed -i "s|ollama|{Put here your ollama variant}|g" flake.nix`

```
nix run . -- --generate_with_llava
nix run . -- --generate_with_gemma
nix run . -- --generate_with_qwen
nix run . -- --generate_with_ministral
```

Note : you can stop at every point. It will resume its calculations at the last image.

Compute the averages :
```
nix run . -- --generate_averages
```

Create the gallery view :
```
nix run . -- --generate_gallery
nix develop .
pdflatex ./gallery.tex -interaction=nonstopmode
```

You now have all the files in pdf. You can create your own report !

## On other systems

This might or might not work as I did everything on NixOS.

Clear the examples graphs : `rm *.pdf`

Install dependencies :
* ollama
* Python and pip
* your favorite LaTeX distribution

Install the project :
```
pip install .
```

Generate the values. This might take some time as it uses multiple ML models and repeats the prompt for a more accurate count. For compairon, this took a few hours on my RTX3070ti.

```
hairloss --generate_with_llava
hairloss --generate_with_gemma
hairloss --generate_with_qwen
hairloss --generate_with_ministral
```

Note : you can stop at every point. It will resume it's calculations at the last image.

Run the averages :
```
hairloss --generate_averages
```

Create the gallery view :
```
hairloss --generate_gallery
pdflatex ./gallery.tex -interaction=nonstopmode
```

You now have all the files in pdf. You can create your own report !
