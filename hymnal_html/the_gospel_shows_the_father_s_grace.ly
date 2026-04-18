\version "2.22.1"

\header {
  title = "246  The Gospel Shows The Father's Grace"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key f \major
  \time 6/4
}

upper = {
  \global
  <<
    { \voiceOne f'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } }\mf a'2 c''4 a'2 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } } } a'4 b'4 c''2 | d''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } c''2 a'4 \acciaccatura { a'16 f'16 } g'2 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } f'4 e'4 f'2 | g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } a'2 a'4 \acciaccatura { a'16 f'16 } g'2 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } c''4 b'4 c''2 | a'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } bes'2 a'4 g'2 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "viii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } f'4 e'4 \acciaccatura { g'16 e'16 } f'2 | }
    { \voiceTwo r1. | <a bes d' f'>1.\arpeggio | <c' e'>1.\arpeggio | <bes, c e g>1.\arpeggio | <bes c' e'>1.\arpeggio | <bes c' e' g'>1.\arpeggio | <f a c'>1.\arpeggio | <a d'>1.\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { f,8 } <c e g>1.\p\arpeggio | \acciaccatura { c,8 } <bes, c e g>4\arpeggio c8 e8 g8 c8 e8 g8 c8 e8 c4 | \acciaccatura { bes,,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 d8 f8 d8 f8 bes,4 | \acciaccatura { c,8 } <c e f a>4\arpeggio e8 f8 a8 e8 f8 a8 e8 f8 d4 | \acciaccatura { c,8 } <c e f a>4\arpeggio e8 f8 a8 e8 f8 a8 e8 f8 c4 | \acciaccatura { c,8 } <c e f a>4\arpeggio e8 f8 a8 e8 f8 a8 e8 f8 g,4 | \acciaccatura { f,8 } <c e g>4\arpeggio e8 g8 e8 g8 e8 g8 e8 g8 d4 | \acciaccatura { c,8 } <c e g>1.\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
