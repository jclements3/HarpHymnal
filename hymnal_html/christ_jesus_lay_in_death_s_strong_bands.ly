\version "2.22.1"

\header {
  title = "048  Christ Jesus Lay In Death's Strong Bands"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key d \minor
  \time 4/4
}

upper = {
  \global
  <<
    { \voiceOne a'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } }\mf g'4 a'4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } d''4 c''4 b'4 | a'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } a'8 f'4 \acciaccatura { a'16 f'16 } g'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } g'8 f'8 e'4 d'4 | a'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } g'4 \acciaccatura { bes'16 g'16 } a'4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } d''4 c''4 b'4 | a'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } a'8 f'4 \acciaccatura { a'16 f'16 } g'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } g'8 f'8 e'4 d'4 | d'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } f'4 g'4 \acciaccatura { e'16 c'16 } d'4 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } g'4 a'4. a'8 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } c''4 d''4 \acciaccatura { f''16 d''16 } e''4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" "7" } } } b'4 a'4. a'8 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } a'4 c''4 g'4 | f'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } d'8 e'4 d'2 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } g'8 f'8 e'4 \acciaccatura { e'16 c'16 } d'4 | }
    { \voiceTwo <d' f'>1\p\arpeggio | <f' a'>1\arpeggio | <g bes d'>1\arpeggio | bes1 | <d' f'>1\arpeggio | <f' a'>1\arpeggio | <g bes d'>1\arpeggio | bes1 | <d f a>1\arpeggio | d'1 | <bes d' f'>1\arpeggio | <f g bes d'>1\arpeggio | <d' f'>1\arpeggio | <d f a>1\arpeggio | c'1 | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { d,8 } <bes, d f>1\p\arpeggio | \acciaccatura { f,8 } <d, f, a,>4\arpeggio f,8 a,8 f,8 a,8 bes,4 | \acciaccatura { a,,8 } <f, a, c>4\arpeggio a,8 c8 a,8 c8 f,4 | \acciaccatura { g,,8 } <e, g, bes,>4\arpeggio g,8 bes,8 g,8 bes,8 e,4 | \acciaccatura { d,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 bes,4 | \acciaccatura { f,8 } <d, f, a,>4\arpeggio f,8 a,8 f,8 a,8 bes,4 | \acciaccatura { a,,8 } <f, a, c>4\arpeggio a,8 c8 a,8 c8 f,4 | \acciaccatura { g,,8 } <e, g, bes,>4\arpeggio g,8 bes,8 g,8 bes,8 e,4 | \acciaccatura { d,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 bes,4 | \acciaccatura { f,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 e4 | \acciaccatura { d,8 } <f, a, c>4\arpeggio a,8 c8 a,8 c8 f,4 | \acciaccatura { a,,8 } <f, a, c e>4\arpeggio a,8 c8 e8 a,8 g,4 | \acciaccatura { f,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 e4 | \acciaccatura { d,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 g,4 | \acciaccatura { f,8 } <d, f, a, bes,>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
