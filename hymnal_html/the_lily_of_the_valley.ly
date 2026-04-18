\version "2.22.1"

\header {
  title = "249  The Lily of the Valley"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key f \major
  \time 6/8
}

upper = {
  \global
  <<
    { \voiceOne f'16^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } }\mf c''8 a'16 c''4 c''8 a'2 c''8 d''4 | f'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } d'8 g'4 c'4. f'8 f'4 f'4 | g'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } a'8 a'4 d''4 a'8 c''8 \acciaccatura { bes'16 g'16 } a'4 a'4 | f'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } g'2. g'4. f'4 | a'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } c''8 c''4 c''8 a'2 c''8 \acciaccatura { e''16 c''16 } d''4 | f'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } d'8 g'4 c'4. f'8 f'4 f'4 | g'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } f'8 a'4 g'4 a'8 g'8 g'4 f'4 | e'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } f'2. f'4. f'4 | bes'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } f'8 bes'8 bes'4 d''2 bes'4 | d''8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } a'8 d''8 c''4. c''4 \acciaccatura { d''16 bes'16 } c''4 a'4 | g'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } f'8 f'4 d''4 f'8 c''8 f'4 a'4 | f'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } g'2. g'4. \acciaccatura { g'16 e'16 } f'4 | a'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } c''8 c''8 c''8 c''4 a'2 d''4 | f'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "6" } } } d'8 g'4 c'4. f'8 f'4 f'4 | g'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } f'8 a'4 g'4 a'8 g'8 g'4 f'4 | e'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "6" } } } \acciaccatura { g'16 e'16 } f'2. f'4. | }
    { \voiceTwo <bes d'>2.\p\arpeggio | bes2. | f'2. | <f a c'>2.\arpeggio | f'2. | <f a>2.\arpeggio | <bes c' e'>2.\arpeggio | <e f a c'>2.\arpeggio | <bes d'>2.\arpeggio | <g' bes'>2.\arpeggio | <bes c' e'>2.\arpeggio | <f a c'>2.\arpeggio | <bes d' f'>2.\arpeggio | <a e'>2.\arpeggio | <bes d'>2.\arpeggio | <a c'>2.\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { f,8 } <f, a, c>2.\p\arpeggio | \acciaccatura { f,8 } <f, a, c>4\arpeggio a,8 c8 g,4 | \acciaccatura { f,8 } <c e g>4\arpeggio e8 g8 c4 | \acciaccatura { c,8 } <c e g>4\arpeggio e8 g8 g,4 | \acciaccatura { f,8 } <c e g>4\arpeggio e8 g8 c4 | \acciaccatura { f,8 } <c e g>4\arpeggio e8 g8 d4 | \acciaccatura { c,8 } <c e f a>4\arpeggio e8 f8 g,4 | \acciaccatura { f,8 } <f, a, bes, d>4\arpeggio a,8 bes,8 c4 | \acciaccatura { bes,,8 } <f, a, c>4\arpeggio a,8 c8 g,4 | \acciaccatura { f,8 } <f, a, c>4\arpeggio a,8 c8 f,4 | \acciaccatura { f,8 } <c e f a>4\arpeggio e8 f8 d4 | \acciaccatura { c,8 } <c e g>4\arpeggio e8 g8 c4 | \acciaccatura { f,8 } <f, a, c>4\arpeggio a,8 c8 c4 | \acciaccatura { bes,,8 } <bes, d f g>4\arpeggio d8 f8 c4 | \acciaccatura { bes,,8 } <f, a, c>4\arpeggio a,8 c8 g,4 | \acciaccatura { f,8 } <bes, d f g>2.\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
