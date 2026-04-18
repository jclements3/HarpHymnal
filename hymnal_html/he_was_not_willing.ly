\version "2.22.1"

\header {
  title = "093  He Was Not Willing"
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
    { \voiceOne g'8.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } }\mf aes'8. g'16 aes'16 g'8 aes'8 g'8 g'4 g'8 g'8 ees'8 | bes'8.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } c''8 bes'8 bes'16 bes'8 g'8 bes'8 f'4. bes'8 bes'8 | g'8.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } aes'8. g'16 aes'16 g'8 aes'8 g'8 g'4 g'8 g'8 ees'8 | bes'8.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } ees'8 g'8 bes'16 bes'8 f'8 c''8 ees'4. bes'8 g'8 | g'8.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } aes'8. g'16 aes'16 g'8 aes'8 g'8 g'4 g'8 g'8 ees'8 | bes'8.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } ees'8 g'8 bes'16 bes'8 f'8 c''8 ees'4. bes'8 g'8 | c''8.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } g'8. c''16 g'16 c''8 g'8 c''8 g'4 c''8 c''8 g'8 | bes'8.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } f'8. bes'16 g'16 bes'8 a'8 bes'8 bes'4. bes'8 bes'8 | }
    { \voiceTwo <ees g bes>2.\p\arpeggio | ees'2. | <ees g bes>2.\arpeggio | r2. | <ees g bes>2.\arpeggio | r2. | <c' ees'>2.\arpeggio | ees'2. | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { ees,8 } <c ees g>2.\p\arpeggio | \acciaccatura { ees,8 } <c ees g>4\arpeggio ees8 g8 f4 | \acciaccatura { ees,8 } <c ees g>4\arpeggio ees8 g8 f4 | \acciaccatura { ees,8 } <c ees g>4\arpeggio ees8 g8 f4 | \acciaccatura { ees,8 } <c ees g>4\arpeggio ees8 g8 f4 | \acciaccatura { ees,8 } <c ees g>4\arpeggio ees8 g8 d4 | \acciaccatura { c,8 } <bes, d f>4\arpeggio d8 f8 c4 | \acciaccatura { bes,,8 } <bes, d f>2.\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
