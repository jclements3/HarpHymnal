\version "2.22.1"

\header {
  title = "058  Come, Your Heart and Voices Raising"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key f \major
  \time 3/4
}

upper = {
  \global
  <<
    { \voiceOne f'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } }\mf a'4 | c''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } a'4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } c''4 d''4 | c''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } \acciaccatura { a'16 f'16 } g'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } bes'4 c''4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } a'4 g'4 | f'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } d'4 | e'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } c'4 | a'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } \acciaccatura { c''16 a'16 } bes'4 | c''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } d''4 | c''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } g'4 | a'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } f'4 | bes'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } bes'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } g'4 f'4 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } d'4 e'4 | \acciaccatura { g'16 e'16 } f'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } | }
    { \voiceTwo <f a c'>2.\p\arpeggio | <c' e' g'>2.\arpeggio | <bes d' f'>2.\arpeggio | <e' bes'>2.\arpeggio | <g bes d'>2.\arpeggio | <d' f'>2.\arpeggio | <d f a>2.\arpeggio | <f a>2.\arpeggio | <e g bes c'>2.\arpeggio | <e' g' bes'>2.\arpeggio | <a c' e'>2.\arpeggio | <a c' e'>2.\arpeggio | <a c' e'>2.\arpeggio | <a c' e'>2.\arpeggio | <g bes>2.\arpeggio | <bes d'>2.\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { f,8 } <c e g>2.\p\arpeggio | \acciaccatura { c,8 } <bes, d f>4\arpeggio d8 f8 c4 | \acciaccatura { bes,,8 } <f, a, c>4\arpeggio a,8 c8 g,4 | \acciaccatura { f,8 } <f, a, c d>4\arpeggio a,8 c8 f,4 | \acciaccatura { f,8 } <f, a, c>4\arpeggio a,8 c8 a,4 | \acciaccatura { g,,8 } <g, bes, d>4\arpeggio bes,8 d8 e4 | \acciaccatura { d,8 } <c e g>4\arpeggio e8 g8 d4 | \acciaccatura { c,8 } <c e g>4\arpeggio e8 g8 g,4 | \acciaccatura { f,8 } <f, a, c d>4\arpeggio a,8 c8 f,4 | \acciaccatura { f,8 } <f, a, c d>4\arpeggio a,8 c8 g,4 | \acciaccatura { f,8 } <f, a, c>4\arpeggio a,8 c8 bes,4 | \acciaccatura { a,,8 } <g, bes, d>4\arpeggio bes,8 d8 a,4 | \acciaccatura { g,,8 } <g, bes, d>4\arpeggio bes,8 d8 bes,4 | \acciaccatura { a,,8 } <g, bes, d>4\arpeggio bes,8 d8 a,4 | \acciaccatura { g,,8 } <f, a, c>4\arpeggio a,8 c8 g,4 | \acciaccatura { f,8 } <f, a, c>2.\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
