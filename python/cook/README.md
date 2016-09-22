# Bake Cakes Into Movie Parts
Cakes are delicious building stones of a final moive. This package contains functions about how to render a cake.

# Cake
Each `cake` has layers, layers are overlayed on each other and then produce a final cake.

Each `layer` has its video source, time to start, time to stop, effects on itself.

When they are overlayed on each other, they also have effects, not simply layed on each other.

# Bake
The way we make the `cake` is called `bake`. Currently we are baking by calling ffmpeg command line.

The intermediate result is the commandline string to be run by bash.
