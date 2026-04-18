\version "2.22.1"

\header {
  title = "231  Souls of Men! Why Will Ye Scatter"
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
    { \voiceOne g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } }\mf fis'8 e'8 d'4 g'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } g'8 a'8 b'4 \acciaccatura { a'16 fis'16 } g'4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } b'8 a'8 b'4 a'8 g'8 | fis'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vii" "°" } } } g'8 a'8 fis'8 \acciaccatura { a'16 fis'16 } g'2 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } fis'8 e'8 d'4 g'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } g'8 a'8 b'4 \acciaccatura { a'16 fis'16 } g'4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } b'8 a'8 b'4 a'8 g'8 | fis'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } g'8 a'8 fis'8 \acciaccatura { a'16 fis'16 } g'2 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } a'8 b'8 c''4 b'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } aes'4 a'4 a'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "viii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } b'8 c''8 d''4 \acciaccatura { a'16 fis'16 } g'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } g'8 fis'8 e'4 d'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } fis'8 e'8 d'4 \acciaccatura { a'16 fis'16 } g'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } g'8 a'8 b'4 g'4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } b'8 a'8 b'4 a'8 g'8 | fis'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } g'8 a'8 fis'8 \acciaccatura { a'16 fis'16 } g'2 | }
    { \voiceTwo c'1\p | <c' e'>1\arpeggio | fis'1 | <g b d'>1\arpeggio | c'1 | <c' e'>1\arpeggio | fis'1 | <fis a c'>1\arpeggio | e'1 | <d' fis'>1\arpeggio | <b e'>1\arpeggio | c'1 | <fis g b>1\arpeggio | <c' e'>1\arpeggio | fis'1 | c'1 | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { g,,8 } <g, b, d>1\p\arpeggio | \acciaccatura { c,8 } <a, c e>4\arpeggio c8 e8 c8 e8 a,4 | \acciaccatura { a,,8 } <a, c e>4\arpeggio c8 e8 c8 e8 g4 | \acciaccatura { fis,8 } <fis a c'>4\arpeggio a8 c'8 a8 c'8 fis4 | \acciaccatura { g,,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 d4 | \acciaccatura { c,8 } <a, c e>4\arpeggio c8 e8 c8 e8 a,4 | \acciaccatura { a,,8 } <a, c e>4\arpeggio c8 e8 c8 e8 g4 | \acciaccatura { fis,8 } <e g b>4\arpeggio g8 b8 g8 b8 e4 | \acciaccatura { e,8 } <c e g>4\arpeggio e8 g8 e8 g8 d4 | \acciaccatura { c,8 } <c e g>4\arpeggio e8 g8 e8 g8 e4 | \acciaccatura { d,8 } <d fis a>4\arpeggio fis8 a8 fis8 a8 d4 | \acciaccatura { d,8 } <d fis g b>4\arpeggio fis8 g8 b8 fis8 a,4 | \acciaccatura { g,,8 } <g, b, c e>4\arpeggio b,8 c8 e8 b,8 g,4 | \acciaccatura { c,8 } <a, c e>4\arpeggio c8 e8 c8 e8 b,4 | \acciaccatura { a,,8 } <a, c e>4\arpeggio c8 e8 c8 e8 g4 | \acciaccatura { fis,8 } <e g b>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
