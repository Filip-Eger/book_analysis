{pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  packages = with pkgs; [
    python3
    python313Packages.tkinter
    python313Packages.wikipedia
    python313Packages.pillow
    python313Packages.requests
    python313Packages.beautifulsoup4
    python313Packages.nltk
    python313Packages.scikit-learn
    python313Packages.numpy
    python313Packages.matplotlib
    python313Packages.pandas
  ];
}
