\version "2.22.1"

\header {
  title = "109  I Need Thee Every Hour"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key aes \major
  \time 3/4
}

upper = {
  \global
  <<
    { \voiceOne aes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } }\mf c''4. bes'8 | aes'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } g'8 aes'2 | aes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } aes'4. bes'8 | aes'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } } } f'8 \acciaccatura { f'16 des'16 } ees'2 | ees'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } bes'4. c''8 | bes'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } ees'8 \acciaccatura { des''16 bes'16 } c''2 | aes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } g'4. aes'8 | g'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } f'8 ees'2 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } c''4. aes'8 | des''8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" "7" \raise #0.6 \smaller "3" } } } c''8 c''4 bes'2 | bes'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } aes'8 | c''8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } bes'8 bes'4 aes'4 | aes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } aes'4. bes'8 | aes'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } } } f'8 ees'4 aes'4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } } } c''4. aes'8 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" } } } \acciaccatura { bes'16 g'16 } aes'2 | }
    { \voiceTwo <des' f'>2.\p\arpeggio | <des' f'>2.\arpeggio | <des' f'>2.\arpeggio | <c' des'>2.\arpeggio | <aes c'>2.\arpeggio | <aes c'>2.\arpeggio | <aes c' ees'>2.\arpeggio | <aes c'>2.\arpeggio | <aes c' ees'>2.\arpeggio | <des' ees' g'>2.\arpeggio | <des' ees' g'>2.\arpeggio | <des' ees' g'>2.\arpeggio | <g aes c' ees'>2.\arpeggio | <c' des'>2.\arpeggio | <c' des' f'>2.\arpeggio | <ees f aes c'>2.\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { aes,,8 } <aes, c ees>2.\p\arpeggio | \acciaccatura { aes,,8 } <aes, c ees>4\arpeggio c8 ees8 bes,4 | \acciaccatura { aes,,8 } <aes, c ees>4\arpeggio c8 ees8 ees4 | \acciaccatura { des,8 } <des ees g bes>4\arpeggio ees8 g8 des4 | \acciaccatura { ees,8 } <ees g bes>4\arpeggio g8 bes8 f4 | \acciaccatura { ees,8 } <ees g bes>4\arpeggio g8 bes8 ees4 | \acciaccatura { aes,,8 } <ees g bes>4\arpeggio g8 bes8 f4 | \acciaccatura { ees,8 } <ees g bes>4\arpeggio g8 bes8 bes,4 | \acciaccatura { aes,,8 } <f aes c'>4\arpeggio aes8 c'8 f4 | \acciaccatura { f,8 } <ees f aes c'>4\arpeggio f8 aes8 f4 | \acciaccatura { ees,8 } <ees g aes c'>4\arpeggio g8 aes8 f4 | \acciaccatura { ees,8 } <ees g aes c'>4\arpeggio g8 aes8 bes,4 | \acciaccatura { aes,,8 } <aes, c des f>4\arpeggio c8 des8 aes,4 | \acciaccatura { des,8 } <des ees g bes>4\arpeggio ees8 g8 ees4 | \acciaccatura { des,8 } <des ees g bes>4\arpeggio ees8 g8 f4 | \acciaccatura { ees,8 } <ees g bes des'>2.\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
