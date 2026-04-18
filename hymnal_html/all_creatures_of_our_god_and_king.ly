\version "2.22.1"

\header {
  title = "010  All Creatures of Our God and King"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key d \major
  \time 6/4
}

upper = {
  \global
  <<
    { \voiceOne d'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } }\mf d'4 e'4 fis'4 d'4 | fis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } g'4 a'1 | d'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } d'4 e'4 fis'4 d'4 | fis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } g'4 a'1 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } cis''4 b'2 a'2 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } cis''4 b'2 a'2 | d''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } d''4 a'4 a'4 \acciaccatura { a'16 fis'16 } g'4 | fis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } g'4 a'1 | d''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } d''4 a'4 a'4 \acciaccatura { a'16 fis'16 } g'4 | fis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } g'4 a'1 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } fis'4 e'2 d'2 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } fis'4 e'2 d'2 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } cis''4 b'2 a'2 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } cis''4 b'2 a'2 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } fis'4 e'1. | \acciaccatura { e'16 cis'16 } d'1^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } | }
    { \voiceTwo <d fis a>1.\p\arpeggio | d'1. | <d fis a>1.\arpeggio | d'1. | <d' fis'>1.\arpeggio | <d' fis'>1.\arpeggio | <cis' d' fis'>1.\arpeggio | <g b d'>1.\arpeggio | b'1. | d'1. | b1. | b1. | <g cis' e'>1.\arpeggio | <b d' fis'>1.\arpeggio | <e g b>1.\arpeggio | <cis e g a>1.\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { d,8 } <b, d fis>1.\p\arpeggio | \acciaccatura { b,,8 } <b, d fis>4\arpeggio d8 fis8 d8 fis8 d8 fis8 d8 fis8 e4 | \acciaccatura { d,8 } <b, d fis>4\arpeggio d8 fis8 d8 fis8 d8 fis8 d8 fis8 cis4 | \acciaccatura { b,,8 } <b, d fis>4\arpeggio d8 fis8 d8 fis8 d8 fis8 d8 fis8 e4 | \acciaccatura { d,8 } <b, d fis>4\arpeggio d8 fis8 d8 fis8 d8 fis8 d8 fis8 cis4 | \acciaccatura { b,,8 } <b, d fis>4\arpeggio d8 fis8 d8 fis8 d8 fis8 d8 fis8 e4 | \acciaccatura { d,8 } <d, fis, g, b,>4\arpeggio fis,8 g,8 b,8 fis,8 g,8 b,8 fis,8 g,8 d,4 | \acciaccatura { g,,8 } <d, fis, a,>4\arpeggio fis,8 a,8 fis,8 a,8 fis,8 a,8 fis,8 a,8 e,4 | \acciaccatura { d,8 } <d, fis, a,>4\arpeggio fis,8 a,8 fis,8 a,8 fis,8 a,8 fis,8 a,8 d,4 | \acciaccatura { d,8 } <b, d fis>4\arpeggio d8 fis8 d8 fis8 d8 fis8 d8 fis8 cis4 | \acciaccatura { b,,8 } <e, g, b,>4\arpeggio g,8 b,8 g,8 b,8 g,8 b,8 g,8 b,8 fis,4 | \acciaccatura { e,8 } <e, g, b,>4\arpeggio g,8 b,8 g,8 b,8 g,8 b,8 g,8 b,8 cis4 | \acciaccatura { b,,8 } <b, d fis>4\arpeggio d8 fis8 d8 fis8 d8 fis8 d8 fis8 cis4 | \acciaccatura { b,,8 } <e, g, b,>4\arpeggio g,8 b,8 g,8 b,8 g,8 b,8 g,8 b,8 fis,4 | \acciaccatura { e,8 } <d, fis, a,>4\arpeggio fis,8 a,8 fis,8 a,8 fis,8 a,8 fis,8 a,8 e,4 | \acciaccatura { d,8 } <d, fis, a, b,>1.\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
