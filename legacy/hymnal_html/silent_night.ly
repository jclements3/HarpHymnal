\version "2.22.1"

\header {
  title = "228  Silent Night"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key bes \major
  \time 3/4
}

upper = {
  \global
  <<
    { \voiceOne f'8.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } }\mf g'16 f'8 d'4. | f'8.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } g'16 f'8 d'4. | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } c''8 a'4. | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } bes'8 \acciaccatura { g'16 ees'16 } f'4. | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } g'8 bes'8. a'16 g'8 | f'8.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } g'16 f'8 \acciaccatura { ees'16 c'16 } d'4. | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } g'8 bes'8. a'16 g'8 | f'8.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } g'16 f'8 \acciaccatura { ees'16 c'16 } d'4. | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } c''8 ees''8. c''16 a'8 | bes'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } \acciaccatura { ees''16 c''16 } d''4. | bes'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } f'8 d'8 f'8. ees'16 c'8 | \acciaccatura { c'16 a16 } bes2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } | }
    { \voiceTwo bes2.\p | bes2. | <ees' f'>2.\arpeggio | <a bes d'>2.\arpeggio | ees'2. | <a bes>2.\arpeggio | ees'2. | bes2. | <ees' f'>2.\arpeggio | <ees' g'>2.\arpeggio | g'2. | <ees g>2.\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { bes,,8 } <f a c'>2.\p\arpeggio | \acciaccatura { bes,,8 } <f a c'>4\arpeggio a8 c'8 g4 | \acciaccatura { f,8 } <f a bes d'>4\arpeggio a8 bes8 c4 | \acciaccatura { bes,,8 } <bes, d ees g>4\arpeggio d8 ees8 bes,4 | \acciaccatura { ees,8 } <bes, d f>4\arpeggio d8 f8 c4 | \acciaccatura { bes,,8 } <bes, d ees g>4\arpeggio d8 ees8 bes,4 | \acciaccatura { ees,8 } <bes, d f>4\arpeggio d8 f8 c4 | \acciaccatura { bes,,8 } <f a c'>4\arpeggio a8 c'8 f4 | \acciaccatura { f,8 } <f a bes d'>4\arpeggio a8 bes8 c4 | \acciaccatura { bes,,8 } <bes, d f>4\arpeggio d8 f8 bes,4 | \acciaccatura { bes,,8 } <bes, d f>4\arpeggio d8 f8 c4 | \acciaccatura { bes,,8 } <bes, d f>2.\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
