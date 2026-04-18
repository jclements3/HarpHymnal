\version "2.22.1"

\header {
  title = "278  We Give Thee But Thine Own"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key g \major
  \time 4/4
}

upper = {
  \global
  <<
    { \voiceOne d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } }\mf c''4 b'4 a'4 | b'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } c''8 \acciaccatura { c''16 a'16 } b'2. | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } a'4 d'4 e'4 | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } d'2. | d'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } e'4 fis'4 g'4 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } a'4 a'4 \acciaccatura { c''16 a'16 } b'4 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } c''4 b'4 a'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } \acciaccatura { a'16 fis'16 } g'2. | }
    { \voiceTwo g'1\p | <g b d'>1\arpeggio | <g b>1\arpeggio | <g b>1\arpeggio | <g b>1\arpeggio | <fis a c' d'>1\arpeggio | <fis a c' d'>1\arpeggio | <fis a c' d'>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { g,,8 } <d fis a>1\p\arpeggio | \acciaccatura { g,,8 } <d fis a>4\arpeggio fis8 a8 fis8 a8 d4 | \acciaccatura { g,,8 } <d fis a>4\arpeggio fis8 a8 fis8 a8 e4 | \acciaccatura { d,8 } <d fis a>4\arpeggio fis8 a8 fis8 a8 e4 | \acciaccatura { d,8 } <d fis a>4\arpeggio fis8 a8 fis8 a8 a,4 | \acciaccatura { g,,8 } <g, b, d e>4\arpeggio b,8 d8 e8 b,8 g,4 | \acciaccatura { g,,8 } <g, b, d e>4\arpeggio b,8 d8 e8 b,8 a,4 | \acciaccatura { g,,8 } <g, b, d e>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
