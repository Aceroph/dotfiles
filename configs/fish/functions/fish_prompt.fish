function fish_prompt
  echo -n (set_color red)'┌'
  echo -n (set_color -b red && set_color black)'󰣇 '
  echo -n (set_color normal && set_color red)''

  echo -n (set_color yellow)''
  echo -n (set_color black && set_color -b yellow) $PWD
  echo (set_color normal && set_color yellow)''

  echo -n (set_color red)'└' $USER (set_color yellow)'~ '
  echo -n (set_color normal)
end
