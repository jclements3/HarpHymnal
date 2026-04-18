\version "2.22.1"

\header {
  title = "126  Jesus Christ Who Came to Save"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key a \minor
  \time 4/4
}

upper = {
  \global
  <<
    { \voiceOne a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } }\mf a'4 g'4 a'4 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "3" } } } a'4 g'4 fis'4 | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } g'4 a'4 \acciaccatura { c''16 a'16 } b'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } aes'4 a'4 d''4 | a'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } b'8 c''4 b'4 a'4 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } a'4 a'4 \acciaccatura { b'16 g'16 } a'4 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" "7" \raise #0.6 \smaller "2" } } } a'4 g'4 fis'4 | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } g'4 a'4 b'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } aes'4 \acciaccatura { b'16 g'16 } a'2 | }
    { \voiceTwo <f a c'>1\p\arpeggio | <b c' e'>1\arpeggio | <a c'>1\arpeggio | <d' g' b'>1\arpeggio | f'1 | <a c' e'>1\arpeggio | <b c' e'>1\arpeggio | <f a c'>1\arpeggio | <d g b>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { a,,8 } <d f a>1\p\arpeggio | \acciaccatura { f,8 } <c d f a>4\arpeggio d8 f8 a8 d8 f4 | \acciaccatura { e,8 } <f a c'>4\arpeggio a8 c'8 a8 c'8 f4 | \acciaccatura { a,,8 } <f a c'>4\arpeggio a8 c'8 a8 c'8 b4 | \acciaccatura { a,,8 } <c e g>4\arpeggio e8 g8 e8 g8 f4 | \acciaccatura { e,8 } <f a c'>4\arpeggio a8 c'8 a8 c'8 f4 | \acciaccatura { a,,8 } <c e f a>4\arpeggio e8 f8 a8 e8 f4 | \acciaccatura { e,8 } <c e g>4\arpeggio e8 g8 e8 g8 b,4 | \acciaccatura { a,,8 } <f a c'>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
