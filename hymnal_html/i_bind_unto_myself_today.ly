\version "2.22.1"

\header {
  title = "104  I Bind Unto Myself Today"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key bes \major
  \time 3/4
}

upper = {
  \global
  <<
    { \voiceOne d'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } }\mf g'2 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } f'4 d'4 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } bes'4 d''4 | c''8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } bes'8 bes'4 \acciaccatura { bes'16 g'16 } a'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } c''4 a'4 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } f'4 a'4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } \acciaccatura { c''16 a'16 } bes'2 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "viii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } a'4 a'4 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } g'4. a'8 | bes'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } g'8 f'4 d'4 | bes4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } bes'2 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } g'4 a'4 | bes'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } c''8 d''2 | c''8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } d''8 bes'4 \acciaccatura { a'16 f'16 } g'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } g'2 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "6" } } } \acciaccatura { a'16 f'16 } g'4 | }
    { \voiceTwo <g bes>2.\p\arpeggio | <g bes>2.\arpeggio | <d' a'>2.\arpeggio | f'2. | f'2. | <f a c'>2.\arpeggio | <f' a'>2.\arpeggio | <d' g'>2.\arpeggio | bes'2. | bes2. | <d' f'>2.\arpeggio | <bes d'>2.\arpeggio | <bes d' f'>2.\arpeggio | <bes d' f'>2.\arpeggio | <f a c'>2.\arpeggio | <bes d'>2.\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { d,8 } <d f a>2.\p\arpeggio | \acciaccatura { g,8 } <d f a>4\arpeggio f8 a8 ees4 | \acciaccatura { d,8 } <c ees g>4\arpeggio ees8 g8 d4 | \acciaccatura { c,8 } <c ees g>4\arpeggio ees8 g8 c4 | \acciaccatura { f,8 } <c ees g>4\arpeggio ees8 g8 g4 | \acciaccatura { f,8 } <c ees g>4\arpeggio ees8 g8 d4 | \acciaccatura { c,8 } <c ees g>4\arpeggio ees8 g8 c4 | \acciaccatura { f,8 } <f a c'>4\arpeggio a8 c'8 g4 | \acciaccatura { f,8 } <f a c'>4\arpeggio a8 c'8 a4 | \acciaccatura { g,8 } <g bes d'>4\arpeggio bes8 d'8 c'4 | \acciaccatura { bes,,8 } <g bes d'>4\arpeggio bes8 d'8 c'4 | \acciaccatura { bes,,8 } <g bes d'>4\arpeggio bes8 d'8 a4 | \acciaccatura { g,8 } <g bes d'>4\arpeggio bes8 d'8 c'4 | \acciaccatura { bes,,8 } <f a c'>4\arpeggio a8 c'8 f4 | \acciaccatura { f,8 } <c ees g>4\arpeggio ees8 g8 d4 | \acciaccatura { c,8 } <c ees g a>2.\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
