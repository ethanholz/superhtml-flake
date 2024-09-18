{
  pkgs ? import <nixpkgs> {},
  system ? builtins.currentSystem,
}: let
  inherit (pkgs) lib;
  sources = builtins.fromJSON (builtins.readFile ./superhtml.json);
  mkBinaryInstall = {
    url,
    version,
    hash,
    downloaded-system
  }:
    pkgs.stdenvNoCC.mkDerivation {
      name = "superhtml-${version}";
      inherit version;
      src = pkgs.fetchurl {
        inherit url;
        sha256 = hash;
      };
      unpackPhase = ''
        tar -xzf $src
      '';
      installPhase = ''
        mkdir -p $out/bin/
        cp ${downloaded-system}/superhtml $out/bin
      '';
    };
  tagged =
    lib.attrsets.mapAttrs
    (k: v: mkBinaryInstall {inherit (v.${system}) version url hash downloaded-system;})
    sources;
  latest = lib.lists.last (
    builtins.sort
    (x: y: (builtins.compareVersions x y) < 0)
    (builtins.attrNames tagged)
  );
in
  tagged // {"default" = tagged.${latest};}
