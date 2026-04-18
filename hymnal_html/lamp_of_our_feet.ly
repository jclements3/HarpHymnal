\version "2.22.1"

\header {
  title = "141  Lamp of Our Feet"
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
    { \voiceOne b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } }\mf b'4 b'4 | a'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } b'4 | c''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } fis'4 | \acciaccatura { a'16 fis'16 } g'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } | d'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } d'4 d'4 | b'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } a'4 | a'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } c''4 b'4 | a'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } g'4 | fis'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } e'4 | d'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } | d'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } e'4 \acciaccatura { a'16 fis'16 } g'4 | b'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } a'4 | \acciaccatura { a'16 fis'16 } g'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } | }
    { \voiceTwo <a c' e'>2.\p\arpeggio | <d' fis'>2.\arpeggio | <a c' e'>2.\arpeggio | <g b d'>2.\arpeggio | <g b>2.\arpeggio | <g b d'>2.\arpeggio | <d' fis'>2.\arpeggio | <d' fis' a'>2.\arpeggio | <d' fis'>2.\arpeggio | <g b d'>2.\arpeggio | <g b>2.\arpeggio | <fis a c'>2.\arpeggio | <fis a c' d'>2.\arpeggio | <c' e'>2.\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { g,,8 } <g, b, d>2.\p\arpeggio | \acciaccatura { a,,8 } <a, c e>4\arpeggio c8 e8 b,4 | \acciaccatura { a,,8 } <g, b, d>4\arpeggio b,8 d8 a,4 | \acciaccatura { g,,8 } <d fis a>4\arpeggio fis8 a8 d4 | \acciaccatura { d,8 } <d fis a>4\arpeggio fis8 a8 a,4 | \acciaccatura { g,,8 } <d fis a>4\arpeggio fis8 a8 e4 | \acciaccatura { d,8 } <a, c e>4\arpeggio c8 e8 b,4 | \acciaccatura { a,,8 } <a, c e>4\arpeggio c8 e8 b,4 | \acciaccatura { a,,8 } <a, c e>4\arpeggio c8 e8 e4 | \acciaccatura { d,8 } <d fis a>4\arpeggio fis8 a8 e4 | \acciaccatura { d,8 } <d fis a>4\arpeggio fis8 a8 a,4 | \acciaccatura { g,,8 } <g, b, d e>4\arpeggio b,8 d8 g,4 | \acciaccatura { g,,8 } <g, b, d e>4\arpeggio b,8 d8 a,4 | \acciaccatura { g,,8 } <g, b, d>2.\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
