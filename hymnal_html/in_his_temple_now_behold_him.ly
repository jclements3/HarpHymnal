\version "2.22.1"

\header {
  title = "116  In His Temple Now Behold Him"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key g \major
  \time 6/8
}

upper = {
  \global
  <<
    { \voiceOne b'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } }\mf b'2 d''4 g'4 | c''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } fis'2 a'4 d'4 | g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } b'4. a'8 \acciaccatura { b'16 g'16 } a'4 g'4 | fis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } d'2. e'2 | fis'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } fis'2 a'4 d'4 | g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } b'2 \acciaccatura { b'16 g'16 } a'4 g'4 | c''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } a'4. b'8 b'4 g'4 | g'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } e'2. fis'8 fis'2 | aes'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } a'2 g'4 a'4 | fis'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } g'2 \acciaccatura { g'16 e'16 } fis'4 g'4 | e'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } fis'2 e'4 g'4 | g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } g'2. \acciaccatura { g'16 e'16 } fis'4 | }
    { \voiceTwo <c' e'>2.\p\arpeggio | <c' e' g'>2.\arpeggio | <g b d'>2.\arpeggio | <g b>2.\arpeggio | <g b>2.\arpeggio | <fis g b d'>2.\arpeggio | <c' e'>2.\arpeggio | <e g b>2.\arpeggio | <e g b>2.\arpeggio | <d fis a>2.\arpeggio | c'2. | <c' e'>2.\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { g,,8 } <g, b, d>2.\p\arpeggio | \acciaccatura { c,8 } <g, b, d>4\arpeggio b,8 d8 a,4 | \acciaccatura { g,,8 } <d fis a>4\arpeggio fis8 a8 d4 | \acciaccatura { d,8 } <d fis a>4\arpeggio fis8 a8 e4 | \acciaccatura { d,8 } <d fis a>4\arpeggio fis8 a8 a,4 | \acciaccatura { g,,8 } <g, b, c e>4\arpeggio b,8 c8 g,4 | \acciaccatura { c,8 } <a, c e>4\arpeggio c8 e8 b,4 | \acciaccatura { a,,8 } <a, c e>4\arpeggio c8 e8 fis4 | \acciaccatura { e,8 } <d fis a>4\arpeggio fis8 a8 e4 | \acciaccatura { d,8 } <c e g>4\arpeggio e8 g8 c4 | \acciaccatura { c,8 } <g, b, d>4\arpeggio b,8 d8 a,4 | \acciaccatura { g,,8 } <g, b, d>2.\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
