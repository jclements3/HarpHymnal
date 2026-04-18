\version "2.22.1"

\header {
  title = "286  When The Roll Is Called Up Yonder"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key aes \major
  \time 4/4
}

upper = {
  \global
  <<
    { \voiceOne aes'8.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } }\mf bes'16 c''8. c''16 c''8. c''16 c''8. bes'16 | aes'8.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } aes'16 bes'8. aes'16 aes'8. f'16 ees'4 | aes'8.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } bes'16 c''8. c''16 c''8. c''16 c''8. c''16 | bes'8.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } aes'16 bes'2. | aes'8.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } bes'16 c''8. c''16 c''8. c''16 c''8. bes'16 | aes'8.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } aes'16 bes'8. aes'16 aes'8. f'16 ees'4 | aes'8.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } bes'16 c''8. c''16 c''8. aes'16 bes'8. bes'16 | bes'8.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } g'16 aes'2. | c''8.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } des''16 ees''2 ees''8. des''16 | c''8.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } des''16 ees''2 c''4 | c''8.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } } } c''16 des''2 des''8. c''16 | bes'8.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } } } c''16 des''2 bes'4 | c''8.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } } } des''16 ees''2 ees''8. c''16 | bes'8.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } aes'16 aes'2 des''4 | des''8.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } bes'16 c''8. c''16 c''8. aes'16 bes'8. bes'16 | bes'8.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } g'16 \acciaccatura { bes'16 g'16 } aes'2. | }
    { \voiceTwo <des' f'>1\p\arpeggio | des'1 | <aes c' ees'>1\arpeggio | <des' ees' g'>1\arpeggio | <des' f'>1\arpeggio | des'1 | <aes c' ees'>1\arpeggio | <aes c' ees'>1\arpeggio | aes'1 | aes'1 | <c' des' f' aes'>1\arpeggio | <c' des' f' aes'>1\arpeggio | <c' des' f' aes'>1\arpeggio | <ees' g'>1\arpeggio | <des' f'>1\arpeggio | <g bes des' ees'>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { aes,,8 } <aes, c ees>1\p\arpeggio | \acciaccatura { aes,,8 } <aes, c ees>4\arpeggio c8 ees8 c8 ees8 bes,4 | \acciaccatura { aes,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 ees4 | \acciaccatura { ees,8 } <ees g aes c'>4\arpeggio g8 aes8 c'8 g8 bes,4 | \acciaccatura { aes,,8 } <aes, c ees>4\arpeggio c8 ees8 c8 ees8 aes,4 | \acciaccatura { aes,,8 } <aes, c ees>4\arpeggio c8 ees8 c8 ees8 bes,4 | \acciaccatura { aes,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 ees4 | \acciaccatura { aes,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 bes,4 | \acciaccatura { aes,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 bes,4 | \acciaccatura { aes,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 f4 | \acciaccatura { ees,8 } <des ees g bes>4\arpeggio ees8 g8 bes8 ees8 des4 | \acciaccatura { ees,8 } <des ees g bes>4\arpeggio ees8 g8 bes8 ees8 ees4 | \acciaccatura { des,8 } <des ees g bes>4\arpeggio ees8 g8 bes8 ees8 f4 | \acciaccatura { ees,8 } <des f aes>4\arpeggio f8 aes8 f8 aes8 ees4 | \acciaccatura { des,8 } <aes, c ees>4\arpeggio c8 ees8 c8 ees8 bes,4 | \acciaccatura { aes,,8 } <aes, c ees f>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
