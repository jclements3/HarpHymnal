\version "2.22.1"

\header {
  title = "207  Our Father Thou in Heaven Above"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key c \minor
  \time 4/4
}

upper = {
  \global
  <<
    { \voiceOne g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } }\mf g'4 ees'4 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" "7" \raise #0.6 \smaller "2" } } } g'4 ees'4 \acciaccatura { ees'16 c'16 } d'4 | c'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } g'2 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } f'4 bes'4 g'4 | ees'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } f'4 g'2 | g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } bes'4 \acciaccatura { d''16 bes'16 } c''4 | ees''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } d''4 c''4 b'4 | c''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } c''2 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } c''4 bes'4 a'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } } } fis'4 \acciaccatura { aes'16 f'16 } g'2 | c''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" "7" \raise #0.6 \smaller "3" } } } bes'4 a'4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } g'4 g'4 f'4 | ees'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } \acciaccatura { aes'16 f'16 } g'2 | aes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } g'4 ees'4 f'4 | ees'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } d'4 \acciaccatura { d'16 bes16 } c'2 | }
    { \voiceTwo <aes c'>1\p\arpeggio | <d ees g bes>1\arpeggio | <aes ees'>1\arpeggio | <aes c' ees'>1\arpeggio | <aes c'>1\arpeggio | <c' ees'>1\arpeggio | <c' ees' g'>1\arpeggio | <aes c' ees'>1\arpeggio | <ees' g'>1\arpeggio | <ees f aes c'>1\arpeggio | <c' d' f' aes'>1\arpeggio | <g bes d'>1\arpeggio | <ees g bes>1\arpeggio | <aes c'>1\arpeggio | <f bes>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { c,8 } <ees, g, bes,>1\p\arpeggio | \acciaccatura { g,,8 } <ees, g, aes, c>4\arpeggio g,8 aes,8 c8 g,8 ees,4 | \acciaccatura { c,8 } <ees, g, bes,>4\arpeggio g,8 bes,8 g,8 bes,8 aes,4 | \acciaccatura { g,,8 } <ees, g, bes,>4\arpeggio g,8 bes,8 g,8 bes,8 aes,4 | \acciaccatura { g,,8 } <ees, g, bes,>4\arpeggio g,8 bes,8 g,8 bes,8 d,4 | \acciaccatura { c,8 } <aes, c ees>4\arpeggio c8 ees8 c8 ees8 aes,4 | \acciaccatura { ees,8 } <aes, c ees>4\arpeggio c8 ees8 c8 ees8 d4 | \acciaccatura { c,8 } <d, f, aes,>4\arpeggio f,8 aes,8 f,8 aes,8 g,4 | \acciaccatura { f,8 } <d, f, aes,>4\arpeggio f,8 aes,8 f,8 aes,8 aes,4 | \acciaccatura { g,,8 } <f, g, bes, d>4\arpeggio g,8 bes,8 d8 g,8 f,4 | \acciaccatura { f,8 } <d, ees, g, bes,>4\arpeggio ees,8 g,8 bes,8 ees,8 aes,4 | \acciaccatura { g,,8 } <ees, g, bes,>4\arpeggio g,8 bes,8 g,8 bes,8 f,4 | \acciaccatura { ees,8 } <c, ees, g,>4\arpeggio ees,8 g,8 ees,8 g,8 c,4 | \acciaccatura { g,,8 } <ees, g, bes,>4\arpeggio g,8 bes,8 g,8 bes,8 d,4 | \acciaccatura { c,8 } <aes, c ees>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
