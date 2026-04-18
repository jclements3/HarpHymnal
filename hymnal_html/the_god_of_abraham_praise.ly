\version "2.22.1"

\header {
  title = "245  The God of Abraham Praise"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key f \minor
  \time 4/4
}

upper = {
  \global
  <<
    { \voiceOne c'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } }\mf f'4 g'4 aes'4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } c''2. | aes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } bes'4 c''4 \acciaccatura { ees''16 c''16 } des''4 | ees''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } c''2. | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" \raise #0.6 \smaller "3" } } } aes'4 bes'4 c''4 | des''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" \raise #0.6 \smaller "3" } } } ees''4 g'4 \acciaccatura { bes'16 g'16 } aes'4 | des''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } c''2 bes'2 | aes'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } | aes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } c''4 c''4 c''4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } bes'2. | aes'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } g'8 f'8 g'8 aes'8 bes'8 c''4 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" "7" \raise #0.6 \smaller "3" } } } f'4 e'2 | c'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } } } f'4 g'4 aes'4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } c''4 bes'8 c''8 des''4 | c''8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } bes'8 aes'2 g'2 | \acciaccatura { g'16 ees'16 } f'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } | }
    { \voiceTwo des'1\p | <des' f' aes'>1\arpeggio | f'1 | <ees' g' bes'>1\arpeggio | <ees' f'>1\arpeggio | <ees' f' c''>1\arpeggio | g'1 | <bes des' f'>1\arpeggio | <bes des' f'>1\arpeggio | <bes des' f'>1\arpeggio | <g bes des'>1\arpeggio | <f g bes des'>1\arpeggio | <aes bes des'>1\arpeggio | <des' f' aes'>1\arpeggio | <bes ees'>1\arpeggio | <bes, ees g>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { c,8 } <aes, c ees>1\p\arpeggio | \acciaccatura { c,8 } <aes, c ees>4\arpeggio c8 ees8 c8 ees8 g,4 | \acciaccatura { f,8 } <des f aes>4\arpeggio f8 aes8 f8 aes8 des4 | \acciaccatura { aes,,8 } <f, aes, c des>4\arpeggio aes,8 c8 des8 aes,8 bes,4 | \acciaccatura { aes,,8 } <f, g, bes, des>4\arpeggio g,8 bes,8 des8 g,8 bes,4 | \acciaccatura { aes,,8 } <f, g, bes, des>4\arpeggio g,8 bes,8 des8 g,8 f,4 | \acciaccatura { bes,,8 } <f, aes, c>4\arpeggio aes,8 c8 aes,8 c8 bes,4 | \acciaccatura { aes,,8 } <f, aes, c>4\arpeggio aes,8 c8 aes,8 c8 bes,4 | \acciaccatura { aes,,8 } <f, aes, c>4\arpeggio aes,8 c8 aes,8 c8 ees4 | \acciaccatura { des,8 } <f, aes, c>4\arpeggio aes,8 c8 aes,8 c8 bes,4 | \acciaccatura { aes,,8 } <f, aes, c>4\arpeggio aes,8 c8 aes,8 c8 c4 | \acciaccatura { bes,,8 } <g, aes, c ees>4\arpeggio aes,8 c8 ees8 aes,8 des4 | \acciaccatura { c,8 } <bes, c ees g>4\arpeggio c8 ees8 g8 c8 c4 | \acciaccatura { bes,,8 } <g, bes, des>4\arpeggio bes,8 des8 bes,8 des8 g,4 | \acciaccatura { f,8 } <des f aes>4\arpeggio f8 aes8 f8 aes8 g4 | \acciaccatura { f,8 } <des f aes>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
