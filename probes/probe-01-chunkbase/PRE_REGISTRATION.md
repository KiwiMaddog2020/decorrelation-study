# Probe 01 pre-registration: Chunkbase village lookup (Minecraft Bedrock)

Frozen before the human pass. The git timestamp on this file is the honesty anchor.

## The flow

A first-time user wants to find the nearest village to their spawn point in an existing
Minecraft **Bedrock** world, using Chunkbase (chunkbase.com), then navigate to it in
game.

Step decomposition (the shared spine both passes score against):

1. Arrive at chunkbase.com and find the right tool among the apps.
2. Open the Seed Map app.
3. Set the platform and version to Bedrock and the matching game version.
4. Find and enter the world seed.
5. Read the map and locate village markers among the structure icons.
6. Read a village's coordinates.
7. Translate those coordinates into in-game navigation.

## Hypotheses (frozen)

- **H-A (false alarm exists).** The model pass flags at least one friction point the
  human does not actually feel, because models over-weight documented or theoretical
  complexity.
- **H-B (miss exists).** The human hits at least one friction the model did not predict.
- **H-C (the residue claim).** The model's misses cluster on **lived-knowledge** friction
  (state not present in the UI text, known only from having used it before), not on
  **visible-in-UI** friction. Specific prediction: the Bedrock-version-lag problem
  (Chunkbase's Bedrock support trails the game, so a subtly wrong map looks correct until
  you are standing in the wrong place) is a lived-knowledge miss the model does not name.

## What would make H-C wrong

If the model predicts the version-lag friction (or any lived-knowledge friction) on its
own, or if the human's only un-predicted frictions turn out to be plainly visible on
screen, then the residue claim fails for this flow: the model reached the friction from
outside and no lived pass was needed.

## Procedure

The model pass (`model_pass.md`) is written and frozen before the human pass. The human
(Kevin) runs the flow without reading the model pass. Scoring (`SCORE.md`) happens only
after both files are frozen.
