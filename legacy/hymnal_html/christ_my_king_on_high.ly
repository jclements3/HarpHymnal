\version "2.22.1"

\header {
  title = "049  Christ My King On High"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key bes \major
  \time 4/4
}

upper = {
  \global
  <<
    { \voiceOne f'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } }\mf f'4 | bes'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vii" "°" } } } \acciaccatura { bes'16 g'16 } a'4 | a'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } bes'4 | g'1^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } | f'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } d'4 | d'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } c'4 bes4 | d'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" } } } ees'4 | c'1^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "viii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } | f'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } \acciaccatura { g'16 ees'16 } f'4 | bes'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vii" "°" } } } a'4 | a'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } bes'4 | g'1^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } | f'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } d'4 | d'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } c'4 bes4 | d'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } c'4 | \acciaccatura { c'16 a16 } bes1^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } | }
    { \voiceTwo <bes d'>1\p\arpeggio | <bes d' f'>1\arpeggio | <a c' ees'>1\arpeggio | <g bes d'>1\arpeggio | <d f a>1\arpeggio | <f a>1\arpeggio | <f g bes>1\arpeggio | <d g bes>1\arpeggio | <bes d'>1\arpeggio | <bes d' f'>1\arpeggio | <a c' ees'>1\arpeggio | <g bes d'>1\arpeggio | <d f a>1\arpeggio | <f a>1\arpeggio | <bes, d f>1\arpeggio | <ees g>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { f,8 } <f a c'>1\p\arpeggio | \acciaccatura { bes,,8 } <a c' ees'>4\arpeggio c'8 ees'8 c'8 ees'8 a4 | \acciaccatura { a,8 } <g bes d'>4\arpeggio bes8 d'8 bes8 d'8 a4 | \acciaccatura { g,8 } <d f a>4\arpeggio f8 a8 f8 a8 ees4 | \acciaccatura { d,8 } <c ees g>4\arpeggio ees8 g8 ees8 g8 d4 | \acciaccatura { c,8 } <c ees g>4\arpeggio ees8 g8 ees8 g8 g4 | \acciaccatura { f,8 } <f a c' ees'>4\arpeggio a8 c'8 ees'8 a8 g4 | \acciaccatura { f,8 } <f a c'>4\arpeggio a8 c'8 a8 c'8 g4 | \acciaccatura { f,8 } <f a c'>4\arpeggio a8 c'8 a8 c'8 f4 | \acciaccatura { bes,,8 } <a c' ees'>4\arpeggio c'8 ees'8 c'8 ees'8 bes4 | \acciaccatura { a,8 } <g bes d'>4\arpeggio bes8 d'8 bes8 d'8 a4 | \acciaccatura { g,8 } <d f a>4\arpeggio f8 a8 f8 a8 ees4 | \acciaccatura { d,8 } <c ees g>4\arpeggio ees8 g8 ees8 g8 d4 | \acciaccatura { c,8 } <c ees g>4\arpeggio ees8 g8 ees8 g8 g4 | \acciaccatura { f,8 } <f a c'>4\arpeggio a8 c'8 a8 c'8 c4 | \acciaccatura { bes,,8 } <bes, d f>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
