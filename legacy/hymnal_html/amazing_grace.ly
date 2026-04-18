\version "2.22.1"

\header {
  title = "022  Amazing Grace"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key g \major
  \time 3/4
}

upper = {
  \global
  <<
    { \voiceOne d'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } }\mf g'2 | b'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } g'8 b'2 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } g'2 | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } \acciaccatura { e'16 c'16 } d'2 | d'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } g'2 | b'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } g'8 b'2 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } \acciaccatura { e''16 c''16 } d''2. | d''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } d''4. b'8 | d''8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } b'8 g'2 | d'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } e'4. g'8 | g'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } e'8 \acciaccatura { e'16 c'16 } d'2 | d'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } g'2 | b'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } g'8 b'2 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } g'2. | \acciaccatura { a'16 fis'16 } g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } | }
    { \voiceTwo <g b>2.\p\arpeggio | <g b d'>2.\arpeggio | <d' fis'>2.\arpeggio | <c e g>2.\arpeggio | <g b>2.\arpeggio | <g b d'>2.\arpeggio | <c' d' fis'>2.\arpeggio | <fis' a' c''>2.\arpeggio | <fis' a' c''>2.\arpeggio | <fis' a' c''>2.\arpeggio | <fis g b>2.\arpeggio | c'2. | <fis a c'>2.\arpeggio | <g b d'>2.\arpeggio | <c' d' fis'>2.\arpeggio | <c' e'>2.\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { g,,8 } <d fis a>2.\p\arpeggio | \acciaccatura { g,,8 } <d fis a>4\arpeggio fis8 a8 e4 | \acciaccatura { d,8 } <c e g>4\arpeggio e8 g8 d4 | \acciaccatura { c,8 } <g, b, d>4\arpeggio b,8 d8 g,4 | \acciaccatura { g,,8 } <d fis a>4\arpeggio fis8 a8 a,4 | \acciaccatura { g,,8 } <d fis a>4\arpeggio fis8 a8 e4 | \acciaccatura { d,8 } <d fis g b>4\arpeggio fis8 g8 d4 | \acciaccatura { g,,8 } <g, b, d e>4\arpeggio b,8 d8 a,4 | \acciaccatura { g,,8 } <g, b, d e>4\arpeggio b,8 d8 a,4 | \acciaccatura { g,,8 } <g, b, d e>4\arpeggio b,8 d8 a,4 | \acciaccatura { g,,8 } <g, b, c e>4\arpeggio b,8 c8 d4 | \acciaccatura { c,8 } <g, b, d>4\arpeggio b,8 d8 g,4 | \acciaccatura { g,,8 } <g, b, d e>4\arpeggio b,8 d8 a,4 | \acciaccatura { g,,8 } <d fis a>4\arpeggio fis8 a8 e4 | \acciaccatura { d,8 } <d fis g b>4\arpeggio fis8 g8 a,4 | \acciaccatura { g,,8 } <g, b, d>2.\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
