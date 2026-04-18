\version "2.22.1"

\header {
  title = "174  Now Rest Beneath Night's Shadow"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key g \major
  \time 4/4
}

upper = {
  \global
  <<
    { \voiceOne b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } }\mf g'4 a'4 b'8 c''8 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } c''2 \acciaccatura { c''16 a'16 } b'4 | b'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } c''8 d''4 d''4 a'4 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } g'2 fis'4 | d'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" } } } g'4 a'4 \acciaccatura { c''16 a'16 } b'4 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } a'2. | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } g'4 a'4 b'8 c''8 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" \raise #0.6 \smaller "2" } } } c''2 b'4 | b'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } c''8 d''4 d''4 \acciaccatura { b'16 g'16 } a'4 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } g'2 fis'4 | d'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } g'4 a'4 b'4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } b'4 a'4 \acciaccatura { a'16 fis'16 } g'4 | }
    { \voiceTwo <g b d'>1\p\arpeggio | g'1 | <e' g'>1\arpeggio | <d' a'>1\arpeggio | e'1 | <d' fis'>1\arpeggio | <b d' fis'>1\arpeggio | <d' e' g'>1\arpeggio | <c' fis'>1\arpeggio | e'1 | e'1 | fis'1 | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { g,,8 } <e g b>1\p\arpeggio | \acciaccatura { g,,8 } <e g b>4\arpeggio g8 b8 g8 b8 e4 | \acciaccatura { e,8 } <b, d fis>4\arpeggio d8 fis8 d8 fis8 c4 | \acciaccatura { b,,8 } <b, d fis>4\arpeggio d8 fis8 d8 fis8 e4 | \acciaccatura { d,8 } <d fis a c'>4\arpeggio fis8 a8 c'8 fis8 d4 | \acciaccatura { d,8 } <b, d fis>4\arpeggio d8 fis8 d8 fis8 c4 | \acciaccatura { b,,8 } <a, c e>4\arpeggio c8 e8 c8 e8 a,4 | \acciaccatura { a,,8 } <e g a c'>4\arpeggio g8 a8 c'8 g8 fis4 | \acciaccatura { e,8 } <e g b>4\arpeggio g8 b8 g8 b8 e4 | \acciaccatura { e,8 } <b, d fis>4\arpeggio d8 fis8 d8 fis8 c4 | \acciaccatura { b,,8 } <b, d fis>4\arpeggio d8 fis8 d8 fis8 fis4 | \acciaccatura { e,8 } <e g b>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
