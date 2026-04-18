\version "2.22.1"

\header {
  title = "151  Lord Jesus Think On Me"
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
    { \voiceOne f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } }\mf aes'4 aes'4 g'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } \acciaccatura { g'16 ees'16 } f'2. | aes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } aes'4 aes'4 bes'4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } c''2. | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } ees''4 ees''4 des''4 | des''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } c''4 c''4 bes'4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } bes'4 aes'4 g'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } \acciaccatura { g'16 ees'16 } f'2. | }
    { \voiceTwo <f aes c'>1\p\arpeggio | <f aes c'>1\arpeggio | <f aes c'>1\arpeggio | <aes c' ees'>1\arpeggio | aes'1 | <aes c' ees'>1\arpeggio | <des' f'>1\arpeggio | <bes ees'>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { f,8 } <des f aes>1\p\arpeggio | \acciaccatura { f,8 } <des f aes>4\arpeggio f8 aes8 f8 aes8 des4 | \acciaccatura { f,8 } <des f aes>4\arpeggio f8 aes8 f8 aes8 bes,4 | \acciaccatura { aes,,8 } <f, aes, c>4\arpeggio aes,8 c8 aes,8 c8 bes,4 | \acciaccatura { aes,,8 } <f, aes, c>4\arpeggio aes,8 c8 aes,8 c8 bes,4 | \acciaccatura { aes,,8 } <f, aes, c>4\arpeggio aes,8 c8 aes,8 c8 des4 | \acciaccatura { c,8 } <aes, c ees>4\arpeggio c8 ees8 c8 ees8 g,4 | \acciaccatura { f,8 } <des f aes>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
