\version "2.22.1"

\header {
  title = "293  You Parents Hear What Jesus Taught"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key f \major
  \time 3/2
}

upper = {
  \global
  <<
    { \voiceOne f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } }\mf a'4 c''4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } g'4 a'4 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } c''4 d''4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } a'4 \acciaccatura { a'16 f'16 } g'4 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } f'4 e'4 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } g'4 \acciaccatura { bes'16 g'16 } a'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } g'4 c''4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } b'4 c''4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } bes'4 \acciaccatura { bes'16 g'16 } a'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } f'4 f'4 | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" } } } \acciaccatura { g'16 e'16 } f'4 | }
    { \voiceTwo r1. | <f a c'>1.\arpeggio | <f' a'>1.\arpeggio | <e' bes'>1.\arpeggio | <bes d'>1.\arpeggio | <f a c'>1.\arpeggio | f'1. | <f' a'>1.\arpeggio | <e g bes c'>1.\arpeggio | <bes c' e'>1.\arpeggio | <c d f a>1.\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { f,8 } <d f a>1.\p\arpeggio | \acciaccatura { f,8 } <d f a>4\arpeggio f8 a8 f8 a8 f8 a8 f8 a8 e4 | \acciaccatura { d,8 } <d f a>4\arpeggio f8 a8 f8 a8 f8 a8 f8 a8 g4 | \acciaccatura { f,8 } <f, a, c d>4\arpeggio a,8 c8 d8 a,8 c8 d8 a,8 c8 f,4 | \acciaccatura { f,8 } <f, a, c>4\arpeggio a,8 c8 a,8 c8 a,8 c8 a,8 c8 g,4 | \acciaccatura { f,8 } <c e g>4\arpeggio e8 g8 e8 g8 e8 g8 e8 g8 c4 | \acciaccatura { f,8 } <c e g>4\arpeggio e8 g8 e8 g8 e8 g8 e8 g8 d4 | \acciaccatura { c,8 } <c e g>4\arpeggio e8 g8 e8 g8 e8 g8 e8 g8 g,4 | \acciaccatura { f,8 } <f, a, c d>4\arpeggio a,8 c8 d8 a,8 c8 d8 a,8 c8 f,4 | \acciaccatura { f,8 } <c e f a>4\arpeggio e8 f8 a8 e8 f8 a8 e8 f8 d4 | \acciaccatura { c,8 } <c e g bes>1.\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
