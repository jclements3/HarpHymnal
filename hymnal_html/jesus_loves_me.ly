\version "2.22.1"

\header {
  title = "131  Jesus Loves Me"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key ees \major
  \time 4/4
}

upper = {
  \global
  <<
    { \voiceOne bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } }\mf g'4 g'4 f'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } bes'4 bes'4 c''4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } ees''4 c''4 c''4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } bes'4 bes'4 \acciaccatura { aes'16 f'16 } g'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } f'4 g'4 bes'4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } c''4 c''4 bes'4 | ees'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } g'4 f'4 \acciaccatura { f'16 d'16 } ees'2 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } g'4 bes'4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } ees''4 bes'4 \acciaccatura { aes'16 f'16 } g'4 | ees'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } g'4 f'4 bes'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } bes'4 c''4 ees''4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } bes'4 ees'4 g'4 | f'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } \acciaccatura { f'16 d'16 } ees'1 | }
    { \voiceTwo <d' ees'>1\p\arpeggio | <d' ees'>1\arpeggio | aes'1 | <d' ees'>1\arpeggio | <d' ees'>1\arpeggio | <d' ees' g'>1\arpeggio | <d ees g bes>1\arpeggio | <d' ees'>1\arpeggio | aes'1 | <aes c'>1\arpeggio | aes'1 | <aes c'>1\arpeggio | <d f aes bes>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { ees,8 } <ees, g, aes, c>1\p\arpeggio | \acciaccatura { ees,8 } <ees, g, aes, c>4\arpeggio g,8 aes,8 c8 g,8 bes,4 | \acciaccatura { aes,,8 } <ees, g, bes,>4\arpeggio g,8 bes,8 g,8 bes,8 f,4 | \acciaccatura { ees,8 } <ees, g, aes, c>4\arpeggio g,8 aes,8 c8 g,8 ees,4 | \acciaccatura { ees,8 } <ees, g, aes, c>4\arpeggio g,8 aes,8 c8 g,8 f,4 | \acciaccatura { ees,8 } <ees, g, aes, c>4\arpeggio g,8 aes,8 c8 g,8 f,4 | \acciaccatura { ees,8 } <ees, g, aes, c>4\arpeggio g,8 aes,8 c8 g,8 ees,4 | \acciaccatura { ees,8 } <ees, g, aes, c>4\arpeggio g,8 aes,8 c8 g,8 bes,4 | \acciaccatura { aes,,8 } <ees, g, bes,>4\arpeggio g,8 bes,8 g,8 bes,8 ees,4 | \acciaccatura { ees,8 } <ees, g, bes,>4\arpeggio g,8 bes,8 g,8 bes,8 f,4 | \acciaccatura { ees,8 } <ees, g, bes,>4\arpeggio g,8 bes,8 g,8 bes,8 bes,4 | \acciaccatura { aes,,8 } <ees, g, bes,>4\arpeggio g,8 bes,8 g,8 bes,8 f,4 | \acciaccatura { ees,8 } <ees, g, bes, c>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
