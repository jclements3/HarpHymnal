\version "2.22.1"

\header {
  title = "154  Lord Who Throughout These Forty Days"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key f \major
  \time 4/4
}

upper = {
  \global
  <<
    { \voiceOne f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } }\mf f'4 e'4 f'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } g'4 g'4 f'4 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } bes'4 a'4 \acciaccatura { g'16 e'16 } f'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } a'2. | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } a'4 bes'4 c''4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } f'4 g'4 a'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } g'4 f'4 f'4 | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } \acciaccatura { g'16 e'16 } f'2. | }
    { \voiceTwo <f a c'>1\p\arpeggio | <f a c'>1\arpeggio | <a c' e'>1\arpeggio | <a c' e'>1\arpeggio | f'1 | <f a c'>1\arpeggio | <e g bes c'>1\arpeggio | <e g bes c'>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { f,8 } <d f a>1\p\arpeggio | \acciaccatura { d,8 } <d f a>4\arpeggio f8 a8 f8 a8 g4 | \acciaccatura { f,8 } <f, a, c>4\arpeggio a,8 c8 a,8 c8 f,4 | \acciaccatura { a,,8 } <f, a, c>4\arpeggio a,8 c8 a,8 c8 g,4 | \acciaccatura { f,8 } <c e g>4\arpeggio e8 g8 e8 g8 d4 | \acciaccatura { c,8 } <c e g>4\arpeggio e8 g8 e8 g8 g,4 | \acciaccatura { f,8 } <f, a, c d>4\arpeggio a,8 c8 d8 a,8 g,4 | \acciaccatura { f,8 } <f, a, c d>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
