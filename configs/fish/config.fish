if status is-interactive
    set -U fish_greeting

    alias vpncegep="cd ~/.local/bin/cpyvpn && python3 -m cpyvpn.client -m l -u 2478978 206.123.48.4"

    alias downloadmusic="cd ~/Music && spotdl --bitrate 320k --output ~/Music/ download 'https://open.spotify.com/playlist/435ceNlwyqYVT8euIU01dp?si=3a567b6c1f3242b9'"
end

