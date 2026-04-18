\version "2.22.1"

\header {
  title = "033  Away In A Manger"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key f \major
  \time 3/4
}

upper = {
  \global
  <<
    { \voiceOne c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } }\mf c''4 bes'8 a'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } g'8 \acciaccatura { g'16 e'16 } f'4 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } e'4 d'4 | c'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } c'4 \acciaccatura { d'16 bes16 } c'4 | d'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } c'4 c'4 g'4 | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vii" "°" } } } d'4 c'4 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } a'4 \acciaccatura { d''16 bes'16 } c''4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } bes'8 a'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } g'8 f'4 f'4 | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } d'4 c'4 | c'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } bes'4 a'8 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } a'4 \acciaccatura { a'16 f'16 } g'4 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "viii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } g'4 d'4 | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "viii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } \acciaccatura { g'16 e'16 } f'4 | }
    { \voiceTwo <e' f'>2.\p\arpeggio | d'2. | <f a c'>2.\arpeggio | <e f a>2.\arpeggio | <e g bes>2.\arpeggio | <f a>2.\arpeggio | r2. | f'2. | <f a c'>2.\arpeggio | <d f a>2.\arpeggio | <e' g'>2.\arpeggio | <e g bes>2.\arpeggio | a2. | <a d'>2.\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { f,8 } <f, a, bes, d>2.\p\arpeggio | \acciaccatura { bes,,8 } <bes, d f>4\arpeggio d8 f8 bes,4 | \acciaccatura { d,8 } <d f a>4\arpeggio f8 a8 g4 | \acciaccatura { f,8 } <f, a, bes, d>4\arpeggio a,8 bes,8 f,4 | \acciaccatura { bes,,8 } <bes, d f>4\arpeggio d8 f8 f4 | \acciaccatura { e,8 } <e g bes>4\arpeggio g8 bes8 g4 | \acciaccatura { f,8 } <d f a>4\arpeggio f8 a8 d4 | \acciaccatura { f,8 } <d f a>4\arpeggio f8 a8 g4 | \acciaccatura { f,8 } <d f a>4\arpeggio f8 a8 e4 | \acciaccatura { d,8 } <a, c e>4\arpeggio c8 e8 bes,4 | \acciaccatura { a,,8 } <a, c e>4\arpeggio c8 e8 f4 | \acciaccatura { e,8 } <c e g>4\arpeggio e8 g8 c4 | \acciaccatura { c,8 } <c e g>4\arpeggio e8 g8 d4 | \acciaccatura { c,8 } <c e g>2.\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
