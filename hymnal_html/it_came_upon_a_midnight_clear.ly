\version "2.22.1"

\header {
  title = "121  It Came Upon A Midnight Clear"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key bes \major
  \time 6/8
}

upper = {
  \global
  <<
    { \voiceOne f'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } }\mf g'8 d''4 f'4 a'8 g'8 c''8 f'4 bes'8 | f'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } d''8 g'8 c''4. a'8 bes'8 bes'8 c''4 c''8 | f'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } g'8 d''4 f'4 a'8 g'8 c''8 f'4 bes'8 | f'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } f'8 g'4 bes'4. g'8 a'8 bes'4 g'8 | d''8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } fis'8 d''4 g'4 d'8 a'8 d'8 bes'4 e'8 | d''8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } g'8 c''8 f'4. bes'8 a'8 g'8 f'4 a'8 | f'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } g'8 d''4 f'4 a'8 g'8 c''8 f'4 bes'8 | f'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } f'8 g'4 bes'4. g'8 a'8 bes'4 g'8 | }
    { \voiceTwo <bes d'>2.\p\arpeggio | <bes d'>2.\arpeggio | <bes d'>2.\arpeggio | <f a c'>2.\arpeggio | r2. | <bes d'>2.\arpeggio | <a c' ees'>2.\arpeggio | <a c' ees'>2.\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { bes,,8 } <f a c'>2.\p\arpeggio | \acciaccatura { bes,,8 } <f a c'>4\arpeggio a8 c'8 f4 | \acciaccatura { bes,,8 } <f a c'>4\arpeggio a8 c'8 g4 | \acciaccatura { f,8 } <d f a>4\arpeggio f8 a8 ees4 | \acciaccatura { d,8 } <d f a>4\arpeggio f8 a8 a4 | \acciaccatura { g,8 } <g bes d'>4\arpeggio bes8 d'8 c'4 | \acciaccatura { bes,,8 } <bes, d f g>4\arpeggio d8 f8 c4 | \acciaccatura { bes,,8 } <bes, d f g>2.\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
