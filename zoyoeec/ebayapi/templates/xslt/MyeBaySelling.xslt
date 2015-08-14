<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:ebay="urn:ebay:apis:eBLBaseComponents"
  xmlns:xs ="http://www.w3.org/2001/XMLSchema">
<xsl:template match="/">
 <ul>
 <xsl:for-each select="//ebay:ItemArray/ebay:Item"> 
  <li>
  <img>
   <xsl:attribute name='src'>
    <xsl:value-of select='ebay:PictureDetails/ebay:GalleryURL'/>
   </xsl:attribute>
  </img>
  <a>
   <xsl:attribute name='href'>/ebay/item/<xsl:value-of select='ebay:ItemID'/></xsl:attribute>
   <xsl:value-of select='ebay:Title'/>
  </a>
  <xsl:value-of select='ebay:PrivateNotes'/>
  </li>
 </xsl:for-each>
 </ul>
</xsl:template>
</xsl:stylesheet>
