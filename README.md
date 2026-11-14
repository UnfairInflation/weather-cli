# weather-cli

Show the current weather for a city in your terminal, with a little ASCII art icon.
Uses the free [Open-Meteo](https://open-meteo.com/) API (no API key needed).

## Usage

```sh
uv run weather.py Copenhagen
uv run weather.py "New York"
```

## Natural-language shortcut (fish shell)

Link the shortcut into your fish config:

```fish
ln -s (path resolve shell/weather.fish) ~/.config/fish/conf.d/weather.fish
```

Open a new terminal, and then you can type:

```fish
weather Copenhagen
What is the weather in Copenhagen?
whats the weather like in New York today
```

When you press Enter, any sentence containing "weather in/for/at <city>" is turned into `weather <city>`.
