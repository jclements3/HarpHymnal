\version "2.22.1"

\header {
  title = "032  Awake, My Soul, And With The Sun"
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
    { \voiceOne g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" "⁷³" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } }\mf g'4 fis'4 | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "+8" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } d'4 g'2 | a'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "6" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } \acciaccatura { c''16 a'16 } b'2. | b'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" } } } b'4 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" } } } a'4 g'4 c''2 | b'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" "²+8" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" } } } \acciaccatura { b'16 g'16 } a'2. | g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } b'4 a'4 g'4 | e'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" } } } fis'2 | g'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" } } } \acciaccatura { e''16 c''16 } d''2 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" } } } g'4 a'4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" } } } b'2 a'2 | \acciaccatura { a'16 fis'16 } g'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } | }
    { \voiceTwo <g b d'>1\p\arpeggio | <e g b>1\arpeggio | <g b d'>1\arpeggio | <c' e' g'>1\arpeggio | <c' e'>1\arpeggio | <d fis a c'>1\arpeggio | <d fis a>1\arpeggio | <d' fis'>1\arpeggio | <c e g b>1\arpeggio | <a c' e'>1\arpeggio | <a c' e'>1\arpeggio | <a c' e' g'>1\arpeggio | <d fis a>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { g,,8 } <d g b e'>1\p\arpeggio | \acciaccatura { e,8 } <d fis a d'>4\arpeggio fis8 a8 d'8 fis8 e4 | \acciaccatura { d,8 } <d fis a b>4\arpeggio fis8 a8 b8 fis8 d4 | \acciaccatura { g,,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 a,4 | \acciaccatura { g,,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 d4 | \acciaccatura { c,8 } <g, c e g>4\arpeggio c8 e8 g8 c8 g,4 | \acciaccatura { d,8 } <c e g>4\arpeggio e8 g8 e8 g8 e4 | \acciaccatura { d,8 } <c e g>4\arpeggio e8 g8 e8 g8 d4 | \acciaccatura { c,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 a,4 | \acciaccatura { g,,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 g,4 | \acciaccatura { g,,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 b,4 | \acciaccatura { a,,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 a,4 | \acciaccatura { g,,8 } <g, b, d>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
