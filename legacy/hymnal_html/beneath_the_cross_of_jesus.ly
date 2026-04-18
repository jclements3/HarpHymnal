\version "2.22.1"

\header {
  title = "039  Beneath The Cross Of Jesus"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key des \major
  \time 4/4
}

upper = {
  \global
  <<
    { \voiceOne aes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } }\mf aes'4. aes'8 g'4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } aes'2 f'4 | des'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } ees'4. f'8 ges'4 | ges'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } \acciaccatura { ges'16 ees'16 } f'2. | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } des''4. des''8 des''4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } bes'4 aes'4 ges'4 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } ees'4. ees'8 e'4 | ees'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } f'2. | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } f'4. ees'8 des'4 | ees'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } f'4 ges'4 aes'4 | aes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } bes'4. bes'8 bes'4 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } ges'2. | ges'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" } } } ges'8 c''4. bes'8 aes'4 | ges'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } f'4 f'4 \acciaccatura { bes'16 ges'16 } aes'4 | ges'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } ges'8 f'4. des'8 f'4 | ees'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } \acciaccatura { ees'16 c'16 } des'2. | }
    { \voiceTwo <c' ees' ges'>1\p\arpeggio | <c' ees' ges'>1\arpeggio | <ges bes>1\arpeggio | <des f aes>1\arpeggio | <ges c' ees'>1\arpeggio | <ges c' ees'>1\arpeggio | <bes des'>1\arpeggio | <f aes c'>1\arpeggio | <ges bes>1\arpeggio | <aes c'>1\arpeggio | <ges bes des'>1\arpeggio | <aes c' ees'>1\arpeggio | <aes bes des' f'>1\arpeggio | <aes c' ees'>1\arpeggio | <ges bes>1\arpeggio | <c ees ges aes>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { des,8 } <des, f, aes, bes,>1\p\arpeggio | \acciaccatura { des,8 } <des, f, aes, bes,>4\arpeggio f,8 aes,8 bes,8 f,8 ees,4 | \acciaccatura { des,8 } <des, f, aes,>4\arpeggio f,8 aes,8 f,8 aes,8 ees,4 | \acciaccatura { des,8 } <bes, des f>4\arpeggio des8 f8 des8 f8 bes,4 | \acciaccatura { bes,,8 } <bes, des f>4\arpeggio des8 f8 des8 f8 c4 | \acciaccatura { bes,,8 } <bes, des f>4\arpeggio des8 f8 des8 f8 c4 | \acciaccatura { bes,,8 } <f, aes, c>4\arpeggio aes,8 c8 aes,8 c8 ges,4 | \acciaccatura { f,8 } <des, f, aes,>4\arpeggio f,8 aes,8 f,8 aes,8 ees,4 | \acciaccatura { des,8 } <des, f, aes,>4\arpeggio f,8 aes,8 f,8 aes,8 aes,4 | \acciaccatura { ges,8 } <ges, bes, des>4\arpeggio bes,8 des8 bes,8 des8 aes,4 | \acciaccatura { ges,8 } <ees, ges, bes,>4\arpeggio ges,8 bes,8 ges,8 bes,8 f,4 | \acciaccatura { ees,8 } <ees, ges, bes,>4\arpeggio ges,8 bes,8 ges,8 bes,8 bes,4 | \acciaccatura { aes,,8 } <aes, c ees ges>4\arpeggio c8 ees8 ges8 c8 bes,4 | \acciaccatura { aes,,8 } <ges, bes, des>4\arpeggio bes,8 des8 bes,8 des8 ges,4 | \acciaccatura { ges,8 } <des, f, aes,>4\arpeggio f,8 aes,8 f,8 aes,8 ees,4 | \acciaccatura { des,8 } <des, f, aes, bes,>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
