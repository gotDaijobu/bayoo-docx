# encoding: utf-8

"""|Document| and closely related objects"""

from __future__ import absolute_import, division, print_function, unicode_literals

from daijdocx.oxml.ns import qn

from daijdocx.blkcntnr import BlockItemContainer
from daijdocx.enum.section import WD_SECTION
from daijdocx.enum.text import WD_BREAK
from daijdocx.section import Section, Sections
from daijdocx.shared import ElementProxy, Emu


class Document(ElementProxy):
    """WordprocessingML (WML) document.

    Not intended to be constructed directly. Use :func:`docx.Document` to open or create
    a document.
    """

    __slots__ = ('_part', '__body')

    def __init__(self, element, part):
        super(Document, self).__init__(element)
        self._part = part
        self.__body = None

    def add_heading(self, text="", level=1):
        """Return a heading paragraph newly added to the end of the document.

        The heading paragraph will contain *text* and have its paragraph style
        determined by *level*. If *level* is 0, the style is set to `Title`. If *level*
        is 1 (or omitted), `Heading 1` is used. Otherwise the style is set to `Heading
        {level}`. Raises |ValueError| if *level* is outside the range 0-9.
        """
        if not 0 <= level <= 9:
            raise ValueError("level must be in range 0-9, got %d" % level)
        style = "Title" if level == 0 else "Heading %d" % level
        return self.add_paragraph(text, style)

    def add_page_break(self):
        """Return newly |Paragraph| object containing only a page break."""
        paragraph = self.add_paragraph()
        paragraph.add_run().add_break(WD_BREAK.PAGE)
        return paragraph

    def add_paragraph(self, text='', style=None):
        """
        Return a paragraph newly added to the end of the document, populated
        with *text* and having paragraph style *style*. *text* can contain
        tab (``\\t``) characters, which are converted to the appropriate XML
        form for a tab. *text* can also include newline (``\\n``) or carriage
        return (``\\r``) characters, each of which is converted to a line
        break.
        """
        return self._body.add_paragraph(text, style)

    def add_picture(self, image_path_or_stream, width=None, height=None):
        """
        Return a new picture shape added in its own paragraph at the end of
        the document. The picture contains the image at
        *image_path_or_stream*, scaled based on *width* and *height*. If
        neither width nor height is specified, the picture appears at its
        native size. If only one is specified, it is used to compute
        a scaling factor that is then applied to the unspecified dimension,
        preserving the aspect ratio of the image. The native size of the
        picture is calculated using the dots-per-inch (dpi) value specified
        in the image file, defaulting to 72 dpi if no value is specified, as
        is often the case.
        """
        run = self.add_paragraph().add_run()
        return run.add_picture(image_path_or_stream, width, height)

    def add_section(self, start_type=WD_SECTION.NEW_PAGE):
        """
        Return a |Section| object representing a new section added at the end
        of the document. The optional *start_type* argument must be a member
        of the :ref:`WdSectionStart` enumeration, and defaults to
        ``WD_SECTION.NEW_PAGE`` if not provided.
        """
        new_sectPr = self._element.body.add_section_break()
        new_sectPr.start_type = start_type
        return Section(new_sectPr, self._part)

    def add_table(self, rows, cols, style=None):
        """
        Add a table having row and column counts of *rows* and *cols*
        respectively and table style of *style*. *style* may be a paragraph
        style object or a paragraph style name. If *style* is |None|, the
        table inherits the default table style of the document.
        """
        table = self._body.add_table(rows, cols, self._block_width)
        table.style = style
        return table

    @property
    def core_properties(self):
        """
        A |CoreProperties| object providing read/write access to the core
        properties of this document.
        """
        return self._part.core_properties

    @property
    def comments_part(self):
        """
        A |Comments| object providing read/write access to the core
        properties of this document.
        """
        return self.part.comments_part
    
    @property
    def footnotes_part(self):
        """
        A |Footnotes| object providing read/write access to the footnotes of this document.
        """
        return self._part._footnotes_part


    @property
    def inline_shapes(self):
        """
        An |InlineShapes| object providing access to the inline shapes in
        this document. An inline shape is a graphical object, such as
        a picture, contained in a run of text and behaving like a character
        glyph, being flowed like other text in a paragraph.
        """
        return self._part.inline_shapes

    @property
    def paragraphs(self):
        """
        A list of |Paragraph| instances corresponding to the paragraphs in
        the document, in document order. Note that paragraphs within revision
        marks such as ``<w:ins>`` or ``<w:del>`` do not appear in this list.
        """
        return self._body.paragraphs

    @property
    def part(self):
        """
        The |DocumentPart| object of this document.
        """
        return self._part

    def save(self, path_or_stream):
        """
        Save this document to *path_or_stream*, which can be either a path to
        a filesystem location (a string) or a file-like object.
        """
        self._part.save(path_or_stream)

    @property
    def sections(self):
        """|Sections| object providing access to each section in this document."""
        return Sections(self._element, self._part)

    @property
    def settings(self):
        """
        A |Settings| object providing access to the document-level settings
        for this document.
        """
        return self._part.settings

    @property
    def styles(self):
        """
        A |Styles| object providing access to the styles in this document.
        """
        return self._part.styles

    @property
    def tables(self):
        """
        A list of |Table| instances corresponding to the tables in the
        document, in document order. Note that only tables appearing at the
        top level of the document appear in this list; a table nested inside
        a table cell does not appear. A table within revision marks such as
        ``<w:ins>`` or ``<w:del>`` will also not appear in the list.
        """
        return self._body.tables

    @property
    def elements(self):
        return self._body.elements
    
    @property
    def abstractNumIds(self):
        """
        Returns list of all the 'w:abstarctNumId' of this document
        """
        return self._body.abstractNumIds
    
    @property
    def last_abs_num(self):
        last = self.abstractNumIds[-1]
        val = last.attrib.get(qn('w:abstractNumId'))
        return  last, val
    
    @property
    def _block_width(self):
        """
        Return a |Length| object specifying the width of available "writing"
        space between the margins of the last section of this document.
        """
        section = self.sections[-1]
        return Emu(
            section.page_width - section.left_margin - section.right_margin
        )

    @property
    def _body(self):
        """
        The |_Body| instance containing the content for this document.
        """
        if self.__body is None:
            self.__body = _Body(self._element.body, self)
        return self.__body

    @property
    def footnotes(self):
        """
        Returns a list of Footnote objects for all footnotes in the document.
        """
        footnotes_part = self.footnotes_part
        footnotes_elm = footnotes_part.element
        from daijdocx.text.footnote import Footnote
        # Only return footnotes with a paragraph (skip separators, etc.)
        return [Footnote(fn, footnotes_elm) for fn in footnotes_elm.findall('.//w:footnote', {'w': footnotes_elm.nsmap['w']}) if fn.find('.//w:p', {'w': footnotes_elm.nsmap['w']}) is not None]

    def get_footnoteReferenceById(self, id):
        """
        Find the paragraph containing a <w:footnoteReference w:id="id"/> and return it as a Paragraph object.
        """
        # Get the document XML root
        body_elm = self._element.body
        # Use findall to get all footnoteReference elements
        refs = body_elm.findall('.//w:footnoteReference', body_elm.nsmap)
        ref = None
        for r in refs:
            if r.get('{%s}id' % body_elm.nsmap['w']) == str(id):
                ref = r
                break
        if ref is None:
            return None
        # Find ancestor <w:p>
        p_elm = ref.getparent()
        while p_elm is not None and p_elm.tag != '{%s}p' % body_elm.nsmap['w']:
            p_elm = p_elm.getparent()
        if p_elm is None:
            return None
        from daijdocx.text.paragraph import Paragraph
        return Paragraph(p_elm, self)




class _Body(BlockItemContainer):
    """
    Proxy for ``<w:body>`` element in this document, having primarily a
    container role.
    """
    def __init__(self, body_elm, parent):
        super(_Body, self).__init__(body_elm, parent)
        self._body = body_elm

    def clear_content(self):
        """
        Return this |_Body| instance after clearing it of all content.
        Section properties for the main document story, if present, are
        preserved.
        """
        self._body.clear_content()
        return self
