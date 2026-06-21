{
  description = "Tracks hairloss over time";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils}:
  flake-utils.lib.eachDefaultSystem (system:
  let
    pkgs = import nixpkgs { inherit system; config.allowUnfree = true; };
  in {
    packages.hairloss = pkgs.python314Packages.buildPythonApplication {
      pname = "hairloss";
      version = "0.1";
      src = ./.;
      pyproject = true;

      build-system = with pkgs.python314Packages; [ setuptools ];

      dependencies = with pkgs; [
        python314Packages.tinydb
        python314Packages.requests
        python314Packages.matplotlib
        python314Packages.numpy
        python314Packages.scipy
        ollama
      ];
      postInstall = ''
        wrapProgram $out/bin/hairloss \
          --set HAIRLOSS_IMAGES "PathToYourLocalGitClone/Images"
      '';

      mainProgram = "hairloss.py";
    };
    packages.default = self.packages.${system}.hairloss;
    devShells = {
      default = pkgs.mkShell {
        packages = with pkgs; [
          python314Packages.tinydb
          python314Packages.requests
          texliveMedium
        ];
      };
    };
  });
}
