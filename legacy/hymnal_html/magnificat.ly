\version "2.22.1"

\header {
  title = "160  Magnificat"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key f \minor
  \time 3/4
}

upper = {
  \global
  <<
    { \voiceOne f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } }\mf f'8 ees'8 des'4 | c'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } g'4 | aes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } g'4 \acciaccatura { g'16 ees'16 } f'4 | e'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" "7" } } } | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } c''4 c''4 | bes'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } aes'4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } g'2 | aes'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } | ees''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } ees''4 des''4 | c''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } c''4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } bes'4 aes'4 | g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } g'4 | aes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } g'4 \acciaccatura { g'16 ees'16 } f'4 | e'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } c''4 | aes'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } g'8 f'8 | \acciaccatura { g'16 ees'16 } f'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } | }
    { \voiceTwo <des f aes>2.\p\arpeggio | <des f aes>2.\arpeggio | <c' ees'>2.\arpeggio | <aes, bes, des f>2.\arpeggio | <f' aes'>2.\arpeggio | <des' f'>2.\arpeggio | <g bes des'>2.\arpeggio | <aes c' ees'>2.\arpeggio | <aes' c''>2.\arpeggio | <aes c' ees'>2.\arpeggio | <aes c' ees'>2.\arpeggio | <c' ees'>2.\arpeggio | <c' ees'>2.\arpeggio | <des' f' aes'>2.\arpeggio | <bes ees'>2.\arpeggio | <bes, ees g>2.\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { f,8 } <aes, c ees>2.\p\arpeggio | \acciaccatura { f,8 } <aes, c ees>4\arpeggio c8 ees8 des4 | \acciaccatura { c,8 } <aes, c ees>4\arpeggio c8 ees8 aes,4 | \acciaccatura { c,8 } <aes, c ees g>4\arpeggio c8 ees8 bes,4 | \acciaccatura { aes,,8 } <des f aes>4\arpeggio f8 aes8 g4 | \acciaccatura { f,8 } <g, bes, des>4\arpeggio bes,8 des8 c4 | \acciaccatura { bes,,8 } <f, aes, c>4\arpeggio aes,8 c8 bes,4 | \acciaccatura { aes,,8 } <f, aes, c>4\arpeggio aes,8 c8 bes,4 | \acciaccatura { aes,,8 } <f, aes, c>4\arpeggio aes,8 c8 bes,4 | \acciaccatura { aes,,8 } <f, aes, c>4\arpeggio aes,8 c8 bes,4 | \acciaccatura { aes,,8 } <f, aes, c>4\arpeggio aes,8 c8 des4 | \acciaccatura { c,8 } <aes, c ees>4\arpeggio c8 ees8 des4 | \acciaccatura { c,8 } <aes, c ees>4\arpeggio c8 ees8 aes,4 | \acciaccatura { c,8 } <aes, c ees>4\arpeggio c8 ees8 g,4 | \acciaccatura { f,8 } <des f aes>4\arpeggio f8 aes8 g4 | \acciaccatura { f,8 } <des f aes>2.\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
