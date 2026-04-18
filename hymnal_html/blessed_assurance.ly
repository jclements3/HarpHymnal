\version "2.22.1"

\header {
  title = "040  Blessed Assurance"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key d \major
  \time 9/8
}

upper = {
  \global
  <<
    { \voiceOne fis'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } }\mf g'8 e'8 a'8 d'8 b'8 a'4. a'2. a'4. | a'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } b'8 fis'8 a'8 a'8 aes'8 d''4. a'2. cis''4 cis''8 | fis'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } g'8 e'8 a'8 d'8 b'8 a'4. a'2. \acciaccatura { b'16 g'16 } a'4. | d'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } d'8 e'8 e'8 fis'8 cis'8 g'4. d'2. e'4. | a'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } b'8 a'8 b'8 a'8 b'8 d''4. a'2. \acciaccatura { b'16 g'16 } a'4. | a'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } cis''8 a'8 cis''8 a'8 b'8 b'4. cis''2. d''4. | cis''8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } b'8 d''8 a'8 e''8 b'8 d''4. a'2. a'4. | d'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } d'8. e'8 e'16 fis'8 cis'8 g'4. d'2. \acciaccatura { fis'16 d'16 } e'4. | }
    { \voiceTwo cis'4\p | <cis' e' g'>4\arpeggio | cis'4 | <cis e g a>4\arpeggio | <cis' e' g'>4\arpeggio | <cis' e' g'>4\arpeggio | <cis' e' g'>4\arpeggio | <cis e g a>4\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { d,8 } <d, fis, a, b,>4\p\arpeggio | \acciaccatura { d,8 } <d, fis, a, b,>4\arpeggio fis,8 a,8 b,8 fis,8 a,8 e,4 | \acciaccatura { d,8 } <d, fis, a, b,>4\arpeggio fis,8 a,8 b,8 fis,8 a,8 d,4 | \acciaccatura { d,8 } <d, fis, a, b,>4\arpeggio fis,8 a,8 b,8 fis,8 a,8 e,4 | \acciaccatura { d,8 } <d, fis, a, b,>4\arpeggio fis,8 a,8 b,8 fis,8 a,8 d,4 | \acciaccatura { d,8 } <d, fis, a, b,>4\arpeggio fis,8 a,8 b,8 fis,8 a,8 e,4 | \acciaccatura { d,8 } <d, fis, a, b,>4\arpeggio fis,8 a,8 b,8 fis,8 a,8 e,4 | \acciaccatura { d,8 } <d, fis, a, b,>4\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
