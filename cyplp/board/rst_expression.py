import os.path
import StringIO

from docutils.core import publish_parts
from docutils.writers.html4css1 import HTMLTranslator, Writer
from docutils.utils import SystemMessage

from chameleon.tales import StructureExpr
from chameleon.utils import unicode_string
from chameleon.astutil import Symbol

# Stole from https://raw.githubusercontent.com/pypa/readme/master/readme/rst.py
class RSTHTMLTranslator(HTMLTranslator):
    """
    """
    def depart_image(self, node):
        uri = node["uri"]
        ext = os.path.splitext(uri)[1].lower()
        # we need to swap RST's use of `object` with `img` tags
        # see http://git.io/5me3dA
        if ext == ".svg":
            # preserve essential attributes
            atts = {}
            for attribute, value in node.attributes.items():
                # we have no time for empty values
                if value:
                    if attribute == "uri":
                        atts["src"] = value
                    else:
                        atts[attribute] = value

            # toss off `object` tag
            self.body.pop()
            # add on `img` with attributes
            self.body.append(self.starttag(node, "img", **atts))
        self.body.append(self.context.pop())


SETTINGS = {
    # Cloaking email addresses provides a small amount of additional
    # privacy protection for email addresses inside of a chunk of ReST.
    "cloak_email_addresses": True,

    # Prevent a lone top level heading from being promoted to document
    # title, and thus second level headings from being promoted to top
    # level.
    "doctitle_xform": True,

    # Prevent a lone subsection heading from being promoted to section
    # title, and thus second level headings from being promoted to top
    # level.
    "sectsubtitle_xform": True,

    # Set our initial header level
    "initial_header_level": 2,

    # Prevent local files from being included into the rendered output.
    # This is a security concern because people can insert files
    # that are part of the system, such as /etc/passwd.
    "file_insertion_enabled": False,

    # Halt rendering and throw an exception if there was any errors or
    # warnings from docutils.
    "halt_level": 2,

    # Output math blocks as LaTeX that can be interpreted by MathJax for
    # a prettier display of Math formulas.
    "math_output": "MathJax",

    # Disable raw html as enabling it is a security risk, we do not want
    # people to be able to include any old HTML in the final output.
    "raw_enabled": False,

    # Disable all system messages from being reported.
    "report_level": 5,

    # Use typographic quotes, and transform --, ---, and ... into their
    # typographic counterparts.
    "smart_quotes": True,

    # Strip all comments from the rendered output.
    "strip_comments": True,

    # Use the short form of syntax highlighting so that the generated
    # Pygments CSS can be used to style the output.
    "syntax_highlight": "short",
}


def render(raw, stream=None):
    if stream is None:
        # Use a io.StringIO as the warning stream to prevent warnings from
        # being printed to sys.stderr.
        stream = StringIO.StringIO()

    settings = SETTINGS.copy()
    settings["warning_stream"] = stream

    writer = Writer()
    writer.translator_class = RSTHTMLTranslator

    try:
        parts = publish_parts(raw, writer=writer, settings_overrides=settings)
    except SystemMessage:
        rendered = None
    else:
        rendered = parts.get("html_body")

    return rendered or raw, bool(rendered)

class RST(object):
    def __init__(self, value):
        self.done = self.transform(value)

    def __str__(self):
        return unicode_string(self.done)

    __html__ = __repr__ = __str__

    @classmethod
    def transform(cls, value):
        return render(value)[0]

class RSTExpression(StructureExpr):
    wrapper_class = Symbol(RST)
