\version "2.22.1"

\header {
  title = "027  As With Gladness Men of Old"
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
    { \voiceOne g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } }\mf fis'8 g'8 a'4 g'4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } c''4 \acciaccatura { c''16 a'16 } b'2 | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } fis'4 g'4 e'4 | d'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } d'4 d'2 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } fis'8 g'8 a'4 g'4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } c''4 \acciaccatura { c''16 a'16 } b'2 | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } fis'4 g'4 e'4 | d'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } d'4 d'2 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } a'4 g'4 b'4 | d''4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } c''8 \acciaccatura { c''16 a'16 } b'2 | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } fis'4 g'4 c''4 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } a'4 \acciaccatura { a'16 fis'16 } g'2 | }
    { \voiceTwo <c' e'>1\p\arpeggio | <fis' a'>1\arpeggio | c'1 | <fis a c'>1\arpeggio | <c' e'>1\arpeggio | <fis' a'>1\arpeggio | c'1 | <fis a c'>1\arpeggio | <g b d'>1\arpeggio | <d' fis' a'>1\arpeggio | c'1 | <fis a c' d'>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { g,,8 } <g, b, d>1\p\arpeggio | \acciaccatura { c,8 } <c e g>4\arpeggio e8 g8 e8 g8 c4 | \acciaccatura { c,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 a,4 | \acciaccatura { g,,8 } <g, b, d e>4\arpeggio b,8 d8 e8 b,8 a,4 | \acciaccatura { g,,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 d4 | \acciaccatura { c,8 } <c e g>4\arpeggio e8 g8 e8 g8 c4 | \acciaccatura { c,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 a,4 | \acciaccatura { g,,8 } <g, b, d e>4\arpeggio b,8 d8 e8 b,8 a,4 | \acciaccatura { g,,8 } <d fis a>4\arpeggio fis8 a8 fis8 a8 e4 | \acciaccatura { d,8 } <c e g>4\arpeggio e8 g8 e8 g8 c4 | \acciaccatura { c,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 a,4 | \acciaccatura { g,,8 } <g, b, d e>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
