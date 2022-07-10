# Created by: Yoshihiro Ota <ota@j.email.ne.jp>
# $FreeBSD$

PORTNAME=	prdanlz
PORTVERSION=	0.2.2
CATEGORIES=	sysutils python
PKGNAMEPREFIX=	${PYTHON_PKGNAMEPREFIX}

MAINTAINER=	ota@j.email.ne.jp
COMMENT=	Periodic Analysis program

LICENSE=	BSD2CLAUSE
LICENSE_FILE=   ${WRKSRC}/LICENSE

USES=		python
USE_PYTHON=	distutils autoplist

MAKE_ENV=       PYTHONPATH=${WRKSRC}/src/

USE_GITHUB=	yes
GH_ACCOUNT=	uyota
GH_PROJECT=	py-${PORTNAME}
GH_TAGNAME=	v${PORTVERSION}

#DOCSDIR=	${PREFIX}/share/doc/${PKGNAMEPREFIX}${PORTNAME}
#EXAMPLESDIR=	${PREFIX}/share/examples/${PKGNAMEPREFIX}${PORTNAME}
PORTSDOCS=	README.md
PORTSEXAMPLES=	*

OPTIONS_DEFINE=	DOCS EXAMPLES

pre-configure:
	echo 'from setuptools import setup; setup()' > ${WRKSRC}/setup.py

do-install-DOCS-on:
	@${MKDIR} ${STAGEDIR}${DOCSDIR}
	${INSTALL_DATA} ${WRKSRC}/README.md ${STAGEDIR}${DOCSDIR}


post-install-EXAMPLES-on:
	${MKDIR} ${STAGEDIR}${EXAMPLESDIR}
	${INSTALL_DATA} ${WRKSRC}/*.json ${STAGEDIR}${EXAMPLESDIR}

.include <bsd.port.mk>
