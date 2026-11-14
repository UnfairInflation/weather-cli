# Natural-language shortcut for the weather CLI (fish shell).
#
# Install: ln -s (path resolve shell/weather.fish) ~/.config/fish/conf.d/weather.fish
#
#   weather Copenhagen                      -> runs weather.py directly
#   What is the weather in Copenhagen?      -> rewritten to: weather Copenhagen
#
# When you press Enter, the line is checked. If it is a sentence that mentions
# "weather in/for/at <city>" (and doesn't start with a real command), it is
# rewritten to "weather <city>" before running.

# Find weather.py next to this file (works when this file is symlinked into conf.d).
set -g __weather_script (path dirname (path dirname (path resolve (status filename))))/weather.py

function weather --description 'Show the current weather for a city'
    uv run --quiet $__weather_script $argv
end

function __weather_city_from_sentence
    set -l city (string match -ri -g '\bweather\s+(?:like\s+)?(?:in|for|at)\s+(.+)$' -- $argv[1])
    or return 1
    set city (string replace -ri '[?!.\s]+$' '' -- $city)
    set city (string replace -ri '\s+(today|right now|now)$' '' -- $city)
    test -n "$city"; and echo $city
end

function __weather_enter
    set -l line (commandline)
    set -l first (string split -n -f1 ' ' -- $line)
    # Only rewrite plain sentences, never lines that start with a real command.
    if test -n "$first"; and not type -q -- $first
        if set -l city (__weather_city_from_sentence $line)
            commandline -r -- "weather "(string escape -- $city)
        end
    end
    commandline -f execute
end

if status is-interactive
    bind enter __weather_enter
    bind -M insert enter __weather_enter 2>/dev/null
end
