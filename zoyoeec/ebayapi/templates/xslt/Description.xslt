<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:ebay="urn:ebay:apis:eBLBaseComponents"
  xmlns:xs ="http://www.w3.org/2001/XMLSchema">
<xsl:template match="/">
 <ul>
 <xsl:for-each select="//ebay:Item"> 
  <xsl:value-of select='ebay:Description'/>
 </xsl:for-each>
 </ul>
</xsl:template>
</xsl:stylesheet>
