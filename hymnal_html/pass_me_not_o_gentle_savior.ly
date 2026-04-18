\version "2.22.1"

\header {
  title = "211  Pass Me Not, O Gentle Savior"
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
    { \voiceOne c''4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } }\mf bes'8 aes'8. g'16 aes'8. f'16 | ees'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } \acciaccatura { bes'16 g'16 } aes'2 | bes'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } bes'8 aes'4 bes'4 | \acciaccatura { des''16 bes'16 } c''2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } | c''4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } bes'8 aes'8. g'16 aes'8. f'16 | ees'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } \acciaccatura { bes'16 g'16 } aes'2 | bes'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } aes'8 c''4 bes'4 | \acciaccatura { bes'16 g'16 } aes'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" \raise #0.6 \smaller "3" } } } | ees''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" \raise #0.6 \smaller "3" } } } c''2 | bes'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } aes'8 f'2 | ees'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } aes'4 c''4 aes'4 | bes'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } | c''4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } bes'8 aes'8. g'16 aes'8. f'16 | ees'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } aes'2 | bes'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } aes'8 c''4 bes'4 | \acciaccatura { bes'16 g'16 } aes'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } | }
    { \voiceTwo <aes c' ees'>1\p\arpeggio | <aes c'>1\arpeggio | <des' ees' g'>1\arpeggio | <aes c' ees'>1\arpeggio | <aes c' ees'>1\arpeggio | <aes c'>1\arpeggio | <des' ees' g'>1\arpeggio | <g aes c' ees'>1\arpeggio | <g' aes'>1\arpeggio | <bes des'>1\arpeggio | <aes c'>1\arpeggio | <ees' g'>1\arpeggio | des'1 | <aes c'>1\arpeggio | <des' ees' g'>1\arpeggio | <des' f'>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { aes,,8 } <ees g bes>1\p\arpeggio | \acciaccatura { aes,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 ees4 | \acciaccatura { ees,8 } <ees g aes c'>4\arpeggio g8 aes8 c'8 g8 bes,4 | \acciaccatura { aes,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 ees4 | \acciaccatura { aes,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 bes,4 | \acciaccatura { aes,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 ees4 | \acciaccatura { ees,8 } <ees g aes c'>4\arpeggio g8 aes8 c'8 g8 bes,4 | \acciaccatura { aes,,8 } <aes, bes, des f>4\arpeggio bes,8 des8 f8 bes,8 aes,4 | \acciaccatura { aes,,8 } <aes, bes, des f>4\arpeggio bes,8 des8 f8 bes,8 c4 | \acciaccatura { bes,,8 } <aes, c ees>4\arpeggio c8 ees8 c8 ees8 bes,4 | \acciaccatura { aes,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 f4 | \acciaccatura { ees,8 } <des f aes>4\arpeggio f8 aes8 f8 aes8 ees4 | \acciaccatura { des,8 } <aes, c ees>4\arpeggio c8 ees8 c8 ees8 aes,4 | \acciaccatura { aes,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 f4 | \acciaccatura { ees,8 } <ees g aes c'>4\arpeggio g8 aes8 c'8 g8 bes,4 | \acciaccatura { aes,,8 } <aes, c ees>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
