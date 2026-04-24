{pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  packages = with pkgs; [
    python3
    python313Packages.tkinter
    python313Packages.wikipedia
    python313Packages.pillow
    python313Packages.requests
    python313Packages.beautifulsoup4
  ];
}
