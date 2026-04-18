\version "2.22.1"
\header { tagline = ##f }
\paper {
  indent = 0\mm
  line-width = 42\mm
  ragged-right = ##f
  oddHeaderMarkup = ""
  evenHeaderMarkup = ""
  oddFooterMarkup = ""
  evenFooterMarkup = ""
  page-breaking = #ly:one-line-breaking
  system-system-spacing.basic-distance = #0
}

\score {
  \new PianoStaff \with { \remove "Bar_number_engraver" } <<
    \new Staff \with {
      \remove "Time_signature_engraver"
      instrumentName = ""
    } <<
      \new Voice { \voiceOne \clef treble \key bes \major g'4 g'8 bes'8. a'16 g'8 }
      \new Voice { \voiceTwo \key bes \major ees'2. }
    >>
    \new Staff \with {
      \remove "Time_signature_engraver"
    } { \clef bass \key bes \major \acciaccatura { ees8 } <bes d' f'>2.\arpeggio }
  >>
  \layout {
    \context { \Score \remove "Bar_number_engraver" }
  }
}
